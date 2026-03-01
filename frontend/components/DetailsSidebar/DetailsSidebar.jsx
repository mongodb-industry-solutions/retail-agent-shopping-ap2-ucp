import React, { useState, useEffect } from "react";
import { Subtitle } from "@leafygreen-ui/typography";
import Icon from "@leafygreen-ui/icon";
import { palette } from "@leafygreen-ui/palette";
import IconButton from "@leafygreen-ui/icon-button";

import "./detailsSidebar.css";
import { useDispatch, useSelector } from "react-redux";
import { setSidebarWidth } from "@/redux/slices/GlobalSlice";

const DetailsSidebar = ({ selectedMessage, setSelectedMessage }) => {
  const dispatch = useDispatch();
  const sidebarWidth =  useSelector((state) => state.Global.sidebarWidth);
  const [isResizing, setIsResizing] = useState(false);

  const handleMouseDown = () => {
    setIsResizing(true);
  };

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isResizing) return;
      const newWidth = window.innerWidth - e.clientX;
      const maxWidth = Math.floor(window.innerWidth / 2);
      dispatch(setSidebarWidth(Math.min(Math.max(320, newWidth), maxWidth)));
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
          className="d-flex container align-items-center justify-content-between p-3"
          style={{
            borderBottom: `1px solid ${palette.gray.light2}`,
            backgroundColor: palette.green.light3,
          }}
        >
          <div className="d-flex align-items-center gap-2">
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
          <IconButton
            aria-label="Close"
            onClick={() => setSelectedMessage(null)}
          >
            <Icon glyph="X" />
          </IconButton>
        </div>
        <div className="container">
          <p>Work in progress</p>
        </div>
      </div>
    </div>
  );
};

export default DetailsSidebar;
