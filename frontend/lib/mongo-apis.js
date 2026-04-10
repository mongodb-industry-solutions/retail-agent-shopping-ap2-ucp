import { journeys } from "./const/ux-writing";
import store from "@/redux/store";
import {
  setCartMandates,
  setCartMandatesWithTwoSignatures,
  setPaymentMandate,
  setPaymentDocument,
} from "@/redux/slices/MandateLedgerSlice";
import { getJourneyUserAndSessionId } from "./helpers";
import { COLLECTIONS } from "./const/data";

/**
 * Fetches available orders by matching payment documents with their corresponding cart mandates.
 * 
 * This function performs a two-step process:
 * 1. Retrieves all payment documents for the given user/session
 * 2. For each payment, finds the matching cart mandate using payment.cart_mandate.mandate_id
 * 
 * @returns {Promise<Array<{payment: Object, mandate: Object}>>} Array of order objects, each containing:
 *   - payment: The complete payment document
 *   - mandate: The matched cart mandate document with entity_type="CartMandate", status="signed", and 2 signatures
 * 
 * @example
 * const orders = await getAvailableOrdersAPI();
 * // Returns: [{payment: {...}, mandate: {...}}, ...]
 */
export const getAvailableOrdersAPI = async () => {
  try {
    const { userId, sessionId } = getJourneyUserAndSessionId(
      journeys.disputing.id,
    );

    // First, fetch all payment documents
    const payments_requestBody = {
      filter: {
        "metadata.user_id": userId,
        "metadata.session_id": sessionId,
      },
      collectionName: COLLECTIONS.PAYMENTS,
    };

    const payments_response = await fetch(`/api/findDocuments`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payments_requestBody),
    });

    if (!payments_response.ok) {
      throw new Error(`Payments HTTP error! status: ${payments_response.status}`);
    }

    const paymentsData = await payments_response.json();
    const paymentDocuments = paymentsData.documents || [];

    if (paymentDocuments.length === 0) {
      return [];
    }

    // Extract mandate IDs from payment documents
    const mandateIds = paymentDocuments
      .map(payment => payment.cart_mandate?.mandate_id)
      .filter(id => id); // Remove any undefined values

    if (mandateIds.length === 0) {
      return [];
    }

    // Now fetch mandates that match these payment mandate IDs
    const cart_with_mandate_requestBody = {
      filter: {
        "metadata.user_id": userId,
        "metadata.session_id": sessionId,
        entity_type: "CartMandate",
        entity_id: { $in: mandateIds }, // Search for mandates with these specific IDs
        status: "signed",
        signatures: { $size: 2 },
      },
      collectionName: COLLECTIONS.MANDATE_LEDGER,
    };

    const cart_with_mandate_response = await fetch(`/api/findDocuments`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(cart_with_mandate_requestBody),
    });

    if (!cart_with_mandate_response.ok) {
      throw new Error(`Mandates HTTP error! status: ${cart_with_mandate_response.status}`);
    }

    const mandatesData = await cart_with_mandate_response.json();
    const mandateDocuments = mandatesData.documents || [];

    // Match each payment with its corresponding mandate
    const orders = paymentDocuments.map(payment => {
      const matchedMandate = mandateDocuments.find(mandate => 
        mandate.entity_id === payment.cart_mandate?.mandate_id
      );
      
      return {
        payment: payment,
        mandate: matchedMandate || null
      };
    }).filter(order => order.mandate !== null); // Only return orders that have both payment and mandate

    console.log("getAvailableOrdersAPI - Matched orders:", orders);
    return orders;
    
  } catch (error) {
    console.error("Error fetching available orders:", error);
    return []; // Return an empty array on error
  }
};

export async function getCartMandatesAPI(journeyId) {
  const { sessionId, userId } = getJourneyUserAndSessionId(journeyId);
  const requestBody = {
    filter: {
      "metadata.user_id": userId,
      "metadata.session_id": sessionId,
      entity_type: { $in: ["CartMandate", "IntentMandate"] },
    },
    collectionName: COLLECTIONS.MANDATE_LEDGER,
  };
  const response = await fetch(`/api/findDocuments`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(requestBody),
  });

  if (!response.ok)
    return {
      error: true,
      message: `Error fetching cart mandate: ${response.status}`,
      status: response.status,
    };

  const data = await response.json();
  console.log("getCartMandateAPI - Response data:", data);

  store.dispatch(
    setCartMandates({
      journeyId,
      cartMandates: data.documents || [],
    }),
  );

  return data;
}

export async function getCartMandatesWithTwoSignatures(journeyId) {
  const { sessionId, userId } = getJourneyUserAndSessionId(journeyId);
  const requestBody = {
    filter: {
      "metadata.user_id": userId,
      "metadata.session_id": sessionId,
      entity_type: "CartMandate",
      status: "signed",
      signatures: { $size: 2 },
    },
    collectionName: COLLECTIONS.MANDATE_LEDGER,
  };
  const response = await fetch(`/api/findDocuments`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(requestBody),
  });

  if (!response.ok)
    return {
      error: true,
      message: `Error fetching cart mandate: ${response.status}`,
      status: response.status,
    };

  const data = await response.json();
  console.log("getCartMandatesWithTwoSignatures - Response data:", data);

  store.dispatch(
    setCartMandatesWithTwoSignatures({
      journeyId,
      cartMandateWithTwoSignatures: data.documents[0] || null,
    }),
  );

  return data;
}

export async function getPaymentMandate(journeyId) {
  const { sessionId, userId } = getJourneyUserAndSessionId(journeyId);
  const requestBody = {
    filter: {
      "metadata.user_id": userId,
      "metadata.session_id": sessionId,
      entity_type: "PaymentMandate",
      status: "created",
      signatures: { $size: 1 },
    },
    collectionName: COLLECTIONS.MANDATE_LEDGER,
  };
  const response = await fetch(`/api/findDocuments`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(requestBody),
  });

  if (!response.ok)
    return {
      error: true,
      message: `Error fetching payment mandate: ${response.status}`,
      status: response.status,
    };

  const data = await response.json();
  console.log("getPaymentMandate - Response data:", data);

  store.dispatch(
    setPaymentMandate({
      journeyId,
      paymentMandate: data.documents[0] || null,
    }),
  );

  return data;
}

export async function getPaymentDocument(journeyId) {
  let paymentMandate =
    store.getState().MandateLedger.journeysStatus?.[journeyId]?.paymentMandate;
  if (!paymentMandate) {
    await getPaymentMandate(journeyId);
    paymentMandate =
      store.getState().MandateLedger.journeysStatus?.[journeyId]
        ?.paymentMandate;
  }

  if (!paymentMandate) {
    return {
      error: true,
      message: "No payment mandate found",
      status: 404,
    };
  }

  const requestBody = {
    filter: {
      "payment_mandate.mandate_id": paymentMandate.entity_id,
    },
    collectionName: COLLECTIONS.PAYMENTS,
  };
  const response = await fetch(`/api/findDocuments`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(requestBody),
  });

  if (!response.ok)
    return {
      error: true,
      message: `Error fetching payment document: ${response.status}`,
      status: response.status,
    };

  const data = await response.json();
  console.log("getPaymentDocument - Response data:", data);

  store.dispatch(
    setPaymentDocument({
      journeyId,
      paymentDocument: data.documents[0] || null,
    }),
  );

  return data;
}
