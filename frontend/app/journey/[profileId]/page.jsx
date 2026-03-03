"use client";

import React, { useEffect, useState, useRef } from "react";
import { useParams } from "next/navigation";
import { useDispatch } from "react-redux";


import "../journey.css";
import { profiles, chatFlows } from "@/lib/const/ux-writing";
import { addStartedJourney } from "@/redux/slices/GlobalSlice";
import ShoppingAssistantNavbar from "@/components/ShoppingAssistantNavbar/ShoppingAssistantNavbar";
import MessageBubble from "@/components/MessageBubble/MessageBubble";
import DetailsSidebar from "@/components/DetailsSidebar/DetailsSidebar";

export default function JourneyPage() {
  const params = useParams();
  const { profileId } = params;
  const profile = profiles[profileId];
  const dispatch = useDispatch();
  const [messages, setMessages] = useState([]);
  const [selectedMessage, setSelectedMessage] = useState(null);
  const messagesEndRef = useRef(null);

  const flow = chatFlows[profileId] || chatFlows.straightforward;

  useEffect(() => {
    dispatch(addStartedJourney(profileId));
  }, []);

  useEffect(() => {
    const firstMessage = flow.find((m) => m.id === "welcome");
    if (firstMessage) {
      setMessages([{ ...firstMessage, timestamp: new Date() }]);
    }
  }, [profileId, flow]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleOptionClick = (optionId, nextMessageId, optionLabel) => {
    const nextMessage = flow.find((m) => m.id === nextMessageId);

    const userMessage = {
      id: `user-${Date.now()}`,
      type: "user",
      content: optionLabel,
      timestamp: new Date(),
    };

    if (nextMessage) {
      setMessages((prev) => [
        ...prev,
        userMessage,
        { ...nextMessage, timestamp: new Date() },
      ]);
    }
  };

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
        <div
          className="chatbotBody"
          style={{
            flex: 1,
            overflowY: "auto",
            padding: 24,
            maxWidth: 900,
            margin: "0 auto",
            width: "100%",
          }}
        >
          {messages.map((message, index) => (
            <MessageBubble
              setSelectedMessage={setSelectedMessage}
              key={`${message.id}-${index}`}
              messageType={message.type}
              messageContent={message.content}
              messageOptions={message.options}
              onOptionClick={handleOptionClick}
              isLatest={index === messages.length - 1}
              message={message}
            />
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Sidebar */}
      {selectedMessage && (
        <DetailsSidebar 
          selectedMessage={selectedMessage} 
          setSelectedMessage={setSelectedMessage} 
        />
      )}
    </div>
  );
}
