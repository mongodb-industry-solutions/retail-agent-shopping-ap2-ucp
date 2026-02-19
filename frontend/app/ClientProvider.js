"use client";

import { Provider } from "react-redux";
import { useEffect } from "react";
import store from "../redux/store";

export default function ClientProvider({ children }) {
  useEffect(() => {
    sessionStorage.clear();
  }, []);

  return <Provider store={store}>{children}</Provider>
}