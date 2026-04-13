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
import { startSessionAPI } from "@/lib/api";
import ShoppingAssistantNavbar from "@/components/ShoppingAssistantNavbar/ShoppingAssistantNavbar";
import DetailsSidebar from "@/components/DetailsSidebar/DetailsSidebar";
import ChatbotContainer from "@/components/ChatbotContainer/ChatbotContainer";

export default function JourneyPage() {
  const params = useParams();
  const { journeyId } = params;
  const journeysStatus = useSelector(state => state.MandateLedger.journeysStatus[journeyId]) || null;
  const selectedMessage = useSelector(state => state.Global.selectedMessage);
  const dispatch = useDispatch();
  const initializingRef = useRef(false); // Track if initialization is in progress

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
      if (isInitializing || session_id || initializingRef.current) {
        return;
      }

      try {
        if (journeysStatus?.isInitializing) {
          // the start session process is already ongoing
          return;
        }
        
        // Set local flag to prevent duplicate calls
        initializingRef.current = true;
        
        // Set initializing state
        dispatch(setSessionInitializing({ journeyId }));
        
        const sessionResponse = await startSessionAPI(journeyId);
        
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
      } finally {
        // Reset the flag
        initializingRef.current = false;
      }
    };

    if (journeyId) {
      initializeSession();
    }
  }, [journeyId, isInitializing, session_id, journeysStatus?.isInitializing, dispatch]);

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
        <ChatbotContainer journeyId={journeyId} />
      </div>
      {/* Sidebar */}
      {selectedMessage && (
        <DetailsSidebar />
      )}
    </div>
  );
}
