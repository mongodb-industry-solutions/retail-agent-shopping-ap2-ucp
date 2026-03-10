"use client";
import { useDispatch, useSelector } from "react-redux";
import { setHealthStatus } from "@/redux/slices/MandateLedgerSlice";
import { getMandateLedgerServiceHealthAPI } from "@/lib/api"; 
import Button from "@leafygreen-ui/button";
import GuidedIntroManager from "@/components/GuidedIntro/GuidedIntroManager";
import ProfileSelection from "@/components/ProfileSelection.jsx/ProfileSelection";
<<<<<<< HEAD
import { Logo } from "@leafygreen-ui/logo";
=======
>>>>>>> fb64d57ada70a720effbbcd1afd285744a243953

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
<<<<<<< HEAD
      <div className="absolute top-6 left-6 flex items-center gap-2">
        <Logo height={30} color='green-dark-2' />
      </div>
      <GuidedIntroManager />
      <ProfileSelection/>
      {/* <div className="absolute top-8 left-1/2 -translate-x-1/2">
=======
      <GuidedIntroManager />
      <ProfileSelection/>
      <div className="absolute top-8 left-1/2 -translate-x-1/2">
>>>>>>> fb64d57ada70a720effbbcd1afd285744a243953
        <h1 className="mb-3">AP2 + Mandate Ledger Service</h1>
        <Button onClick={getMandateLedgerServiceHealth}>Check Mandate Ledger Health</Button>
        {health && (
          <div className="mt-3">
            <h2>Mandate Ledger Health Status:</h2>
            <pre>{JSON.stringify(health, null, 2)}</pre>
          </div>
        )}
<<<<<<< HEAD
      </div> */}
=======
      </div>
>>>>>>> fb64d57ada70a720effbbcd1afd285744a243953
    </main>
  );
}
