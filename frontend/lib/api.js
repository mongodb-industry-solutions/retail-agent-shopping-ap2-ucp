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

export async function startShoppingSessionAPI(userId) {
  const response = await fetch(`/api/v1/shopping/start-session`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ user_id: userId }),
  });

  if (!response.ok) {
    return {
      error: true,
      message: `Error starting shopping session: ${response.status}`,
      status: response.status,
    };
  }

  const data = await response.json();
  console.log("startShoppingSession res", data);
  return data;
}
