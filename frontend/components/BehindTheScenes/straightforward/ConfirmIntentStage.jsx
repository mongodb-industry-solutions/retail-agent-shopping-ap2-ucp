import { AGENT_ROLE, USER_ROLE } from "@/lib/constants/messages";
import React from "react";
import ImageContainer from "../ImageContainer";
import { Code, Panel } from "@leafygreen-ui/code";
import EmptyStateMessage from "@/components/DetailsSidebar/EmptyStateMessage";

const AskIntentStage = ({ type }) => {
  return (
    <div>
      {type === AGENT_ROLE ? (
        <EmptyStateMessage/>
      ) : (
        <div>
            TODO
        </div>
      )}
    </div>
  );
};

export default AskIntentStage;
