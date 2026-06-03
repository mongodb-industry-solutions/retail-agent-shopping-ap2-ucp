import React, { useEffect, useState } from "react";
import { Modal } from "react-bootstrap";
import Button from "@leafygreen-ui/button";
import { H3, Body, H2 } from "@leafygreen-ui/typography";
import Icon from "@leafygreen-ui/icon";
import { palette } from "@leafygreen-ui/palette";
import { spacing } from "@leafygreen-ui/tokens";
import { getAvailableOrdersAPI } from "@/lib/mongo-apis";
import { useDispatch } from "react-redux";
import { setOrder } from "@/redux/slices/MandateLedgerSlice";
import { setDisputingSystemMessage } from "@/redux/slices/GlobalSlice";
import { auditorPopup, journeys } from "@/lib/const/ux-writing";

const OrderSelectionModal = ({ show, onHide, redirectToStartDisputingJourney }) => {
  const [orders, setOrders] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const dispatch = useDispatch();

  const handleOrderSelection = (order) => {
    dispatch(setOrder({journeyId: journeys.disputing.id , order}));
    dispatch(setDisputingSystemMessage({ order }));
    redirectToStartDisputingJourney();
  };

  useEffect(() => {
    const fetchAvailableOrders = async () => {
        setIsLoading(true);
      const response = await getAvailableOrdersAPI();
      console.log("Available orders response:", response);
      setOrders(response);
      setIsLoading(false);
    };
    fetchAvailableOrders();
  }, []);

  return (
    <Modal
      show={show}
      onHide={onHide}
      size="lg"
      fullscreen={false}
      backdrop="static"
      keyboard={false}
    >
      <Modal.Header
        closeButton
        style={{
          backgroundColor: palette.yellow.light2,
          border: "none",
          padding: spacing[4],
        }}
      >
        <div className="d-flex align-items-center" style={{ gap: spacing[3] }}>
          <div
            style={{
              backgroundColor: palette.yellow.base,
              borderRadius: "13px",
              padding: spacing[3],
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Icon glyph="Warning" size="large" fill={palette.yellow.dark2} />
          </div>
          <div>
            <H2 style={{ margin: 0, marginBottom: spacing[1] }}>
              Start Audit Process
            </H2>
            <Body style={{ color: palette.gray.dark1, margin: 0, fontSize: "16px" }}>
              {auditorPopup.startText}
            </Body>
          </div>
        </div>
      </Modal.Header>
      <Modal.Body style={{ padding: spacing[4] }}>
        {/* AP2 Cryptographic Audit Trail Info */}
        <div
          className="mb-4 p-4 rounded"
          style={{
            backgroundColor: palette.blue.light3,
            border: `1px solid ${palette.blue.light2}`,
          }}
        >
          <div className="d-flex align-items-start" style={{ gap: spacing[3] }}>
            <Icon glyph="Checkmark" size="large" fill={palette.blue.base} />
            <div>
              <H3 style={{ margin: 0, marginBottom: spacing[2] }}>
                AP2 Cryptographic Audit Trail
              </H3>
              <Body style={{ fontSize: "16px", color: palette.gray.dark1, margin: 0 }}>
                {auditorPopup.bannerText}
              </Body>
            </div>
          </div>
        </div>

        {/* Order Selection */}
        <div>
          <Body
            weight="medium"
            className="mb-3"
            style={{
              color: palette.gray.dark1,
              textTransform: "uppercase",
              fontSize: "14px",
              letterSpacing: "0.5px",
            }}
          >
            SELECT AN ORDER TO AUDIT
          </Body>
          {
            isLoading && (
              <div className="d-flex align-items-center justify-content-center" style={{ height: "150px" }}>
                <Icon glyph="Spinner" size="large" fill={palette.gray.base} />
              </div>
            )
          }

          {
            !isLoading && orders.length === 0 && (
              <div 
                className="d-flex flex-column align-items-center justify-content-center text-center p-5"
                style={{ 
                  height: "200px",
                  backgroundColor: palette.gray.light3,
                  borderRadius: "8px",
                  border: `1px solid ${palette.gray.light1}`
                }}
              >
                <H3 style={{ margin: spacing[3] + " 0 " + spacing[2] + " 0", color: palette.gray.dark1 }}>
                  No Orders Available
                </H3>
                <Body style={{ color: palette.gray.base, fontSize: "16px", maxWidth: "300px", lineHeight: "1.5" }}>
                  You don't have any orders yet. Please complete at least one journey to start an auditing process.
                </Body>
              </div>
            )
          }

          {
            !isLoading && orders.length > 0 && (
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: spacing[2],
                }}
              >
                {orders.map((order) => (
              <div
                key={order?.payment?._id}
                className="border rounded p-3 cursor-pointer"
                style={{
                  border: `1px solid ${palette.gray.light1}`,
                  backgroundColor: "white",
                  cursor: "pointer",
                  transition: "all 0.2s ease",
                }}
                onClick={() => handleOrderSelection(order)}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = palette.gray.light3;
                  e.currentTarget.style.borderColor = palette.gray.light2;
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = "white";
                  e.currentTarget.style.borderColor = palette.gray.light1;
                }}
              >
                <div className="d-flex align-items-center justify-content-between">
                  <div
                    className="d-flex align-items-center"
                    style={{ gap: spacing[3] }}
                  >
                    <Icon
                      glyph="Package"
                      size="large"
                      fill={palette.gray.base}
                    />
                    <div>
                      <H3 style={{ margin: 0, marginBottom: spacing[1] }}>
                        {order?.mandate?.mandate_data?.contents?.payment_request?.details?.display_items[0]?.label}
                      </H3>
                      <div
                        className="d-flex align-items-center"
                        style={{ gap: spacing[2] }}
                      >
                        <Body style={{ color: palette.gray.base, fontSize: "16px", margin: 0 }}>
                          {order?.payment?.processed_at}
                        </Body>
                        <span
                          className="badge rounded-pill"
                          style={{
                            backgroundColor: palette.green.light2,
                            color: palette.green.dark2,
                            fontSize: "13px",
                          }}
                        >
                          {order?.payment?.status}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div
                    className="d-flex align-items-center"
                    style={{ gap: spacing[2] }}
                  >
                    <Body weight="medium" style={{ color: palette.gray.dark2 }}>
                      {order?.payment?.amount} {order?.payment?.currency}
                    </Body>
                    <Icon glyph="ChevronRight" fill={palette.gray.base} />
                  </div>
                </div>
              </div>
            ))}
              </div>
            )
          }
        </div>
      </Modal.Body>
    </Modal>
  );
};

export default OrderSelectionModal;
