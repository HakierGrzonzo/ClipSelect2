import {
  Links,
  LiveReload,
  Meta,
  Outlet,
  Scripts,
  ScrollRestoration,
  useLoaderData,
} from "@remix-run/react";

import { createContext } from "react";
import { json } from "@remix-run/node";
import { Container } from "./components";
import styles from "./base.css";
import { AppClient } from "./client/AppClient";

export const meta = () => ({
  charset: "utf-8",
  title: "ClipSelect2",
  viewport: "width=device-width,initial-scale=1",
});

export function links() {
  return [{ rel: "stylesheet", href: styles }];
}

interface IBackendProps {
  frontendURL: string;
}

export interface IBackendClient extends IBackendProps {
  frontendClient: AppClient;
}
export const loader = () => {
  return json({ frontendURL: process.env.FRONTEND ?? "http://localhost:8000" });
};

export const BackendContext = createContext<IBackendClient>(
  {} as IBackendClient
);

export default function App() {
  const { frontendURL } = useLoaderData() as IBackendProps;
  const frontendClient = new AppClient({ BASE: frontendURL });
  return (
    <html lang="en">
      <head>
        <Meta />

        <Links />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin=""
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Karla:wght@400;700&display=swap"
          rel="stylesheet"
        />
      </head>

      <body>
        <script>
          {/*
           * Declare process as a global, so the code can handle it being undefined
           * Is should only be defined on the backend
           */}
          var process = undefined
        </script>
        <BackendContext.Provider value={{ frontendClient, frontendURL }}>
          <Container>
            <Outlet />
          </Container>
          <Scripts />
        </BackendContext.Provider>

        <ScrollRestoration />

        <LiveReload />
      </body>
    </html>
  );
}
