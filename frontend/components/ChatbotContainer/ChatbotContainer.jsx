import React, { useEffect, useRef } from "react";

import MessageBubble from "../MessageBubble/MessageBubble";
import { useSelector } from "react-redux";
import { chatWithAuditorAgentAPI, chatWithShoppingAgentAPI } from "@/lib/api";
import AgentThinking from "../MessageBubble/AgentThinking";
import { stepHasBehindTheScenes } from "../BehindTheScenes/componentMap";
import { journeys } from "@/lib/const/ux-writing";

const ChatbotContainer = ({ journeyId }) => {
  const messages =
    useSelector((state) => state.Global.messages[journeyId]) || [];
  const agentIsThinking =
    useSelector(
      (state) => state.MandateLedger.journeysStatus[journeyId]?.agentIsThinking,
    ) || false;
  const messagesEndRef = useRef(null);

  const handleOptionClick = async (option) => {
    // Call the API with the selected option
    try {
      if (journeyId === journeys.disputing.id)
        await chatWithAuditorAgentAPI(journeyId, option);
      else 
        await chatWithShoppingAgentAPI(journeyId, option);
    } catch (error) {
      console.error("Error sending message:", error);
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
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
      {messages && messages.length > 0 ? (
        messages.map((message, index) => (
          <MessageBubble
            key={`${message.id}-${index}`}
            onOptionClick={handleOptionClick}
            isLatest={index === messages.length - 1}
            message={message}
            hasBehindTheScenes={stepHasBehindTheScenes(
              journeyId,
              message.step,
              message.type,
            )}
          />
        ))
      ) : (
        <div style={{ padding: "20px", textAlign: "center", opacity: 0.7 }}>
          No messages yet. Starting your shopping session...
        </div>
      )}

      {/* Show thinking message when agent is thinking */}
      {agentIsThinking && <AgentThinking />}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default ChatbotContainer;
