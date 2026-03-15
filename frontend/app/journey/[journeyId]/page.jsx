"use client";

import React, { useEffect, useState, useRef } from "react";
import { useParams } from "next/navigation";
import { useDispatch, useSelector } from "react-redux";

import "../journey.css";
import { addStartedJourney } from "@/redux/slices/GlobalSlice";
import { 
  setSessionInitializing, 
  clearSessionInitializing 
} from "@/redux/slices/MandateLedgerSlice";
import { startShoppingSessionAPI } from "@/lib/api";
import ShoppingAssistantNavbar from "@/components/ShoppingAssistantNavbar/ShoppingAssistantNavbar";
import DetailsSidebar from "@/components/DetailsSidebar/DetailsSidebar";
import ChatbotContainer from "@/components/ChatbotContainer/ChatbotContainer";

export default function JourneyPage() {
  const params = useParams();
  const { journeyId } = params;
  const journeysStatus = useSelector(state => state.MandateLedger.journeysStatus[journeyId]) || null;
  const dispatch = useDispatch();
  const [selectedMessage, setSelectedMessage] = useState(null);

  // Get session state from Redux
  const sessionState = useSelector(state => state.MandateLedger.journeysStatus[journeyId]);
  const { session_id, user_id, isInitializing } = sessionState || {};

  useEffect(() => {
    dispatch(addStartedJourney(journeyId));
  }, []);

  // Start session when page loads (only if not already initialized or initializing)
  useEffect(() => {
    const initializeSession = async () => {
      // Don't start if already initialized, initializing, or session exists
      if (isInitializing || session_id) {
        return;
      }

      try {
        if (journeysStatus.isInitializing) {
          // the start session process is already ongoing
          return;
        }
        // Set initializing state
        dispatch(setSessionInitializing({ journeyId }));
        
        const sessionResponse = await startShoppingSessionAPI(journeyId);
        
        if (sessionResponse.error) {
          console.error("Failed to start session:", sessionResponse.message);
          return;
        }
        
        console.log("Session started for profile", journeyId, ":", {
          sessionId: sessionResponse.session_id,
          userId: sessionResponse.user_id,
          status: sessionResponse.status
        });
      } catch (error) {
        console.error("Error starting session:", error);
        dispatch(clearSessionInitializing({ journeyId }));
      }
    };

    if (journeyId) {
      initializeSession();
    }
  }, [journeyId, dispatch]);

  if (!journeysStatus) {
    return <div>Shopping journey not found.</div>;
  }


  return (
    <div
      className="JourneyPage"
      style={{ height: "100vh", display: "flex", overflow: "hidden" }}
    >
      {/* Main Chat */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
        {/* Header */}
        <ShoppingAssistantNavbar journeyId={journeyId} />
        {/* Messages */}
        <ChatbotContainer journeyId={journeyId} setSelectedMessage={setSelectedMessage}/>
      </div>
      {/* Sidebar */}
      {selectedMessage && (
        <DetailsSidebar selectedMessage={selectedMessage} setSelectedMessage={setSelectedMessage} />
      )}
    </div>
  );
}
