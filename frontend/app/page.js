"use client";
import { useDispatch, useSelector } from "react-redux";
import { setHealthStatus } from "@/redux/slices/MandateLedgerSlice";
import { getMandateLedgerServiceHealthAPI } from "@/lib/api"; 
import Button from "@leafygreen-ui/button";

export default function Home() {
  const dispatch = useDispatch();
  const health = useSelector((state) => state.MandateLedger.healthStatus);

  const getMandateLedgerServiceHealth = async () => {
    try {
      const response = await getMandateLedgerServiceHealthAPI();
      console.log("Mandate Ledger Service Health:", response);
      dispatch(setHealthStatus(response));
    } catch (error) {
      console.error("Error fetching Mandate Ledger Service Health:", error);
    }
  }

  return (
    <main className="flex flex-col min-h-screen items-center justify-center relative">
      <div className="absolute top-8 left-1/2 -translate-x-1/2">
        <h1 className="mb-3">AP2 + Mandate Ledger Service</h1>
        <Button onClick={getMandateLedgerServiceHealth}>Check Mandate Ledger Health</Button>
        {health && (
          <div className="mt-3">
            <h2>Mandate Ledger Health Status:</h2>
            <pre>{JSON.stringify(health, null, 2)}</pre>
          </div>
        )}
      </div>
    </main>
  );
}
