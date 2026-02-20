"use client";

import { Provider } from "react-redux";
import { useEffect } from "react";
import store from "../redux/store";

export default function ClientProvider({ children }) {
  useEffect(() => {
    if (process.env.NODE_ENV === "development") {
      sessionStorage.clear();
    }
  }, []);

  return <Provider store={store}>{children}</Provider>
}