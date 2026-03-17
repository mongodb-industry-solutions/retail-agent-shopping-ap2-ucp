import React, { useEffect, useRef } from "react";

import MessageBubble from "../MessageBubble/MessageBubble";
import { useSelector } from "react-redux";
import { chatWithShoppingAgentAPI } from "@/lib/api";
import AgentThinking from "../MessageBubble/AgentThinking";

const ChatbotContainer = ({ journeyId }) => {
  const messages = useSelector(state => state.Global.messages[journeyId]) || [];  
  const agentIsThinking = useSelector(state => state.MandateLedger.journeysStatus[journeyId]?.agentIsThinking) || false;
  const messagesEndRef = useRef(null);

  const handleOptionClick = async (optionId, nextMessageId, optionLabel) => {
    // Call the API with the selected option
    try {
      await chatWithShoppingAgentAPI(journeyId, optionLabel, optionId);
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
      {messages && messages.length > 0 ? messages.map((message, index) => (
        <MessageBubble
          key={`${message.id}-${index}`}
          messageId={message.id}
          messageType={message.type}
          messageContent={message.content}
          messageOptions={message.messageOptions}
          onOptionClick={handleOptionClick}
          isLatest={index === messages.length - 1}
          bubbleDetails={message.bubbleDetails}
          behindTheScenes={message.behindTheScenes}
        />
      )) : (
        <div style={{ padding: '20px', textAlign: 'center', opacity: 0.7 }}>
          No messages yet. Starting your shopping session...
        </div>
      )}
      
      {/* Show thinking message when agent is thinking */}
      {agentIsThinking && (
        <AgentThinking/>
      )}
      <div ref={messagesEndRef} />

    </div>
  );
};

export default ChatbotContainer;
