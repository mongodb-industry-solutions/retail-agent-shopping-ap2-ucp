"use client";

import React, { useEffect, useState, useRef } from "react";
import { useParams } from "next/navigation";
import { useDispatch, useSelector } from "react-redux";

import "../journey.css";
import { profiles, chatFlows } from "@/lib/const/ux-writing";
import { addStartedJourney } from "@/redux/slices/GlobalSlice";
import { 
  setSessionInitializing, 
  setSessionId, 
  clearSessionInitializing 
} from "@/redux/slices/MandateLedgerSlice";
import { startShoppingSessionAPI } from "@/lib/api";
import ShoppingAssistantNavbar from "@/components/ShoppingAssistantNavbar/ShoppingAssistantNavbar";
import DetailsSidebar from "@/components/DetailsSidebar/DetailsSidebar";
import ChatbotContainer from "@/components/ChatbotContainer/ChatbotContainer";

export default function JourneyPage() {
  const params = useParams();
  const { profileId } = params;
  const profile = profiles[profileId];
  const dispatch = useDispatch();
  const [messages, setMessages] = useState([]);
  const [selectedMessage, setSelectedMessage] = useState(null);

  // Get session state from Redux
  const sessionState = useSelector(state => state.MandateLedger.journeysStatus[profileId]);
  const { session_id, user_id, isInitializing } = sessionState || {};

  // const flow = chatFlows[profileId] || chatFlows.straightforward;

  useEffect(() => {
    dispatch(addStartedJourney(profileId));
  }, []);

  // Start session when page loads (only if not already initialized or initializing)
  useEffect(() => {
    const initializeSession = async () => {
      // Don't start if already initialized, initializing, or session exists
      if (isInitializing || session_id) {
        return;
      }

      try {
        // Set initializing state
        dispatch(setSessionInitializing({ profileId }));
        
        const sessionResponse = await startShoppingSessionAPI();
        
        if (sessionResponse.error) {
          console.error("Failed to start session:", sessionResponse.message);
          dispatch(clearSessionInitializing({ profileId }));
          return;
        }

        // Store session data in Redux
        dispatch(setSessionId({
          profileId,
          session_id: sessionResponse.session_id,
          user_id: sessionResponse.user_id
        }));
        
        console.log("Session started for profile", profileId, ":", {
          sessionId: sessionResponse.session_id,
          userId: sessionResponse.user_id,
          status: sessionResponse.status
        });
      } catch (error) {
        console.error("Error starting session:", error);
        dispatch(clearSessionInitializing({ profileId }));
      }
    };

    if (profileId && profile) {
      initializeSession();
    }
  }, [profileId, profile, dispatch, isInitializing, session_id]);

  // useEffect(() => {
  //   // Only initialize messages once session is ready
  //   if (isSessionInitialized) {
  //     const firstMessage = flow.find((m) => m.id === "welcome");
  //     if (firstMessage) {
  //       setMessages([{ ...firstMessage, timestamp: new Date() }]);
  //     }
  //   }
  // }, [profileId, flow, isSessionInitialized]);





  if (!profile) {
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
        <ShoppingAssistantNavbar profileId={profileId} />
        {/* Messages */}
        <ChatbotContainer messages={messages} setMessages={setMessages}/>
      </div>

      {/* Sidebar */}
      {selectedMessage && (
        <DetailsSidebar selectedMessage={selectedMessage} setSelectedMessage={setSelectedMessage} />
      )}
    </div>
  );
}
