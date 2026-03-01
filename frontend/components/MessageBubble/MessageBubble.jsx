"use client";

import React from 'react'
import { Chip } from "@leafygreen-ui/chip";
import Button from "@leafygreen-ui/button";
import { Body, Subtitle } from "@leafygreen-ui/typography";
import { palette } from "@leafygreen-ui/palette";
import Icon from "@leafygreen-ui/icon";

const MessageBubble = ({
  messageType,
  messageContent,
  messageOptions,
  onOptionClick,
  isLatest,
  message,
  setSelectedMessage,
}) => {

  if (messageType === "user") {
    return (
      <div
        className="speechBubble userBubble d-flex flex-col"
        style={{ backgroundColor: palette.green.dark2 }}
      >
        <Body style={{ color: "white" }} className="text-start messageContent">
          {messageContent}
        </Body>
        <>
          <hr className="m-0" />
          <div
            className="agentDetails"
            style={{ backgroundColor: palette.green.light3 }}
          >
            {/* Agent header for details message */}
            <div className="d-flex justify-content-between">
              <div className="d-flex flex-row align-items-center gap-2">
                <Icon
                  style={{ color: palette.green.dark2 }}
                  glyph="Database"
                ></Icon>
                <Subtitle
                  className={"agentPrefix"}
                  style={{ color: palette.green.dark2 }}
                >
                  Behind The Scenes
                </Subtitle>
              </div>
              <Button
                rightGlyph={<Icon glyph="ArrowRight" />}
                size="small"
                variant="primaryOutlined"
                onClick={() => setSelectedMessage(message)}
              >
                Click for details
              </Button>
            </div>
            {/* Agent content for details message */}
            <div>
              <p className="behindTheScenesSummary m-0">
                {message.behindTheScenes.summary}
              </p>
              <div className="mt-2 flex flex-wrap gap-1.5">
                {message.behindTheScenes.keyPoints.map((point, i) => (
                  <Chip key={i} label={point} className="chip p-1" />
                ))}
              </div>
            </div>
          </div>
        </>
      </div>
    );
  }
  const hasDetails = !!message.detailedInfo;
  return (
    <>
      <div className="agentHeader">
        <img src="/icons/coachGTM_Headshot.png" className="agentImage" alt="Agent headshot" />
        <Subtitle className="agentPrefix">Agent's response</Subtitle>
      </div>
      <div className="speechBubble answerBubble">
        <Body className="messageContent">{messageContent}</Body>
        {/* Message details */}
        {hasDetails && (
          <>
            <hr className="m-0" />
            <div
              className="agentDetails"
              style={{ backgroundColor: palette.gray.light3 }}
            >
              {/* Agent header for details message */}
              <div className="d-flex justify-content-between">
                <div className="d-flex flex-row align-items-center gap-2">
                  <Icon
                    style={{ color: palette.green.dark2 }}
                    glyph="Database"
                  ></Icon>
                  <Subtitle
                    className={"agentPrefix"}
                    style={{ color: palette.green.dark2 }}
                  >
                    Behind The Scenes
                  </Subtitle>
                </div>
                <Button
                  rightGlyph={<Icon glyph="ArrowRight" />}
                  size="small"
                  variant="primaryOutlined"
                  onClick={() => setSelectedMessage(message)}
                >
                  Click for details
                </Button>
              </div>
              {/* Agent content for details message */}
              <div>
                <p className="behindTheScenesSummary m-0">
                  {message.behindTheScenes.summary}
                </p>
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {message.behindTheScenes.keyPoints.map((point, i) => (
                    <Chip key={i} label={point} className="chip p-1" />
                  ))}
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      {isLatest && messageOptions && (
        <div className="d-flex flex-row flex-wrap gap-3">
          {messageOptions.map((option) => (
            <Button
              key={option.id}
              leftGlyph={<Icon glyph="Sparkle" />}
              size="small"
              variant="default"
              onClick={() =>
                onOptionClick(option.id, option.nextMessageId, option.label)
              }
            >
              {option.label}
            </Button>
          ))}
        </div>
      )}
    </>
  );

}

export default MessageBubble