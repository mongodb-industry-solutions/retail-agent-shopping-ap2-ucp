'use client';
import React, { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { Subtitle, Body } from "@leafygreen-ui/typography";
import Icon from "@leafygreen-ui/icon";
import { palette } from "@leafygreen-ui/palette";
import IconButton from "@leafygreen-ui/icon-button";
import {Toggle} from "@leafygreen-ui/toggle";
import { setFollowLatestMessage } from "@/redux/slices/GlobalSlice";
import { useDispatch, useSelector } from "react-redux";
import { getStepComponent } from "@/components/BehindTheScenes/componentMap";
import StageNotImplementedFallback from "./StageNotImplementedFallback";
import EmptyStateMessage from "./EmptyStateMessage";

import "./detailsSidebar.css";
import {
  setSidebarWidth,
  setSelectedMessage,
} from "@/redux/slices/GlobalSlice";
import ShoppingAgentIntroductionStep from "../BehindTheScenes/straightforward/ShoppingAgentIntroductionStep";
import { AGENT_ROLE } from "@/lib/const/bubbleDetails";
import MerchantAgentIntroductionStep from "../BehindTheScenes/straightforward/MerchantAgentIntroductionStep";
import MandatesCreatedStep from "../BehindTheScenes/straightforward/MandatesCreatedStep";
import CartMandateSignedPaymentCredentialsStep from "../BehindTheScenes/straightforward/CartMandateSignedPaymentCredentialsStep";
import PaymentCompletedStep from "../BehindTheScenes/straightforward/PaymentCompletedStep";

const DetailsSidebar = () => {
  const dispatch = useDispatch();
  const params = useParams();
  const { journeyId } = params;
  const sidebarWidth = useSelector((state) => state.Global.sidebarWidth);
  const selectedMessage = useSelector(
    (state) => state.Global.selectedMessage,
  );
  const { type, step } = selectedMessage || {};
  const [isResizing, setIsResizing] = useState(false);
  const [isRowLayout, setIsRowLayout] = useState(false);
  const followLatestMessage = useSelector((state) => state.Global.followLatestMessage);

  // Render behind the scenes component based on step and journey
  const renderBehindTheScenesComponent = () => {
    if (!step || !journeyId) {
      return <EmptyStateMessage />;
    }
    
    const StageComponent = getStepComponent(journeyId, step);
    
    if (StageComponent) {
      return <StageComponent type={type} />;
    }
    
    // Fallback if component not found
    return <StageNotImplementedFallback step={step} />;
  };

  const handleMouseDown = () => {
    setIsResizing(true);
  };

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isResizing) return;
      const newWidth = window.innerWidth - e.clientX;
      const maxWidth = Math.floor(window.innerWidth / 2);
      const finalWidth = Math.min(Math.max(320, newWidth), maxWidth);
      dispatch(setSidebarWidth(finalWidth));
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      document.addEventListener("mousemove", handleMouseMove);
      document.addEventListener("mouseup", handleMouseUp);
    }

    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };
  }, [isResizing, dispatch]);

  // Check if layout should be row or column based on sidebar width
  useEffect(() => {
    const minWidthForRow = 620; // 300px + 320px for both divs
    setIsRowLayout(sidebarWidth >= minWidthForRow);
  }, [sidebarWidth]);

  return (
    <div className="d-flex flex-row h-100">
      {/* Resizer */}
      <div
        style={{
          width: 4,
          cursor: "col-resize",
          background: "#e0e0e0",
          height: "100%",
          zIndex: 2,
        }}
        onMouseDown={handleMouseDown}
      />
      {/* Content */}
      <div
        style={{
          width: sidebarWidth,
          minWidth: 320,
          maxWidth: Math.floor(window.innerWidth / 2),
          borderLeft: "1px solid #e0e0e0",
          overflowY: "auto",
          height: "100%",
          background: "#fff",
        }}
      >
        <div
          className="d-flex flex-column  align-items-center justify-content-between p-3"
          style={{
            borderBottom: `1px solid ${palette.gray.light2}`,
            backgroundColor: palette.green.light3,
          }}
        >
          <div className="w-100 d-flex justify-content-between">
            <div className="d-flex align-items-center gap-2">
              <Icon
                style={{ color: palette.green.dark2 }}
                glyph="Database"
              ></Icon>
              <div className="d-flex align-items-center gap-2">
                <Subtitle
                  className={"agentPrefix"}
                  style={{ color: palette.green.dark2 }}
                >
                  Behind The Scenes
                </Subtitle>
                <div
                  style={{
                    width: "8px",
                    height: "8px",
                    backgroundColor: palette.green.dark1,
                    borderRadius: "50%",
                    border: `2px solid ${palette.green.base}`,
                  }}
                  title="Details for the selected message (green border)"
                ></div>
              </div>
            </div>
            <IconButton
              aria-label="Close"
              onClick={() => dispatch(setSelectedMessage(null))}
            >
              <Icon glyph="X" />
            </IconButton>
          </div>
          
          <div className="w-100 d-flex flex-wrap justify-content-between gap-2 mt-2">
            <div className="left-side" style={{ flex: "0 0 auto", minWidth: "300px", whiteSpace: "nowrap" }}>
              <Body style={{ fontSize: "12px", color: palette.gray.dark1, fontStyle: "italic" }}>
                Showing details for the message with{" "}
                <span 
                  style={{
                    padding: "2px 6px",
                    border: "2px solid #00ff00",
                    borderRadius: "4px",
                    backgroundColor: "rgba(0, 255, 0, 0.1)",
                    color: "black",
                    fontWeight: "500",
                    fontSize: "11px"
                  }}
                >
                  green border
                </span>
              </Body>
            </div>
            <div className={`right-side d-flex ${isRowLayout ? 'justify-content-end' : 'justify-content-start'} align-items-center gap-2`} style={{ flex: "0 0 auto", minWidth: "320px", whiteSpace: "nowrap" }}>
              <Body id="follow-latest-bts-label" style={{ fontSize: "14px" }}>
                Automatically follow the latest message
              </Body>
              <Toggle
                id="toggle"
                size="small"
                aria-labelledby="follow-latest-bts-label"
                checked={followLatestMessage}
                onChange={(checked, event) => {
                  dispatch(setFollowLatestMessage(checked));
                }}
              />
            </div>
          </div>
        </div>
        <div className="container">
          {renderBehindTheScenesComponent()}
        </div>
      </div>
    </div>
  );
};

export default DetailsSidebar;
