import React from "react";
import styles from "./MessageBubble.module.css";
import { Body, Subtitle } from "@leafygreen-ui/typography";

const AgentThinking = () => {
  return (
    <div>
      <div className="agentHeader">
        <img
          src="/icons/ShoppingAgentAP2chatFlow.png"
          className="agentImage"
          alt="Agent headshot"
        />
        <Subtitle className="agentPrefix">Agent's response</Subtitle>
      </div>
      <div className={`speechBubble answerBubble ${styles.thinkingBubble}`}>
        <Body
          className={`messageContent ${styles.thinkingMessage} ${styles.pulse}`}
        >
          Agent is thinking...
          <span className={styles.dots}>...</span>
        </Body>
      </div>
    </div>
  );
};

export default AgentThinking;
