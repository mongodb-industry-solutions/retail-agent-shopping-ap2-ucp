export async function getMandateLedgerServiceHealthAPI() {
  const response = await fetch(`/api/mandateLedgerServiceHealth`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });
  if (!response.ok) {
    return {
      error: true,
      message: `Error fetching mandate ledger service health: ${response.status}`,
      status: response.status,
    };
  }
  let data = await response.json();
  console.log("getMandateLedgerServiceHealth res", data);
  return data;
}

export async function startShoppingSessionAPI(userId, dispatch, profileId) {
  const response = await fetch(`/api/shopping-start-session?user_id=${encodeURIComponent(userId)}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ user_id: userId }),
  });

  if (!response.ok) {
    let error = {
      error: true,
      message: `Error starting shopping session: ${response.status}`,
      status: response.status,
    };
    
    if (dispatch && profileId) {
      const { setSessionInitialationError } = await import('@/redux/slices/MandateLedgerSlice');
      dispatch(setSessionInitialationError({ profileId, error }));
    }

    return error
  }

  const data = await response.json();
  console.log("startShoppingSession res", data);
  return data;
}
