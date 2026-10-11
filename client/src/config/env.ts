/**
 * Application environment configuration.
 * Next.js automatically loads .env / .env.local from the client root directory.
 * Client-accessible variables are prefixed with NEXT_PUBLIC_.
 */

export const ENV = {
  /**
   * Base URL for the FastAPI backend server.
   * Defaults to http://localhost:8000 if not specified.
   */
  API_URL:
    process.env.NEXT_PUBLIC_API_URL ||
    process.env.NEXT_PUBLIC_SERVER_URL ||
    "http://localhost:8000",

  /**
   * Server URL alias for backend communication.
   */
  SERVER_URL:
    process.env.NEXT_PUBLIC_SERVER_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    "http://localhost:8000",

  /**
   * Timeout for API requests in milliseconds.
   * Defaults to 120,000ms (2 minutes).
   */
  API_TIMEOUT_MS:
    Number(process.env.NEXT_PUBLIC_API_TIMEOUT_MS) || 120000,

  /**
   * Application display name.
   */
  APP_NAME:
    process.env.NEXT_PUBLIC_APP_NAME || "SynthaResearch",

  /**
   * Application environment (development, test, production).
   */
  APP_ENV:
    process.env.NEXT_PUBLIC_APP_ENV || process.env.NODE_ENV || "development",

  /**
   * Helper booleans for checking the environment.
   */
  IS_DEV: (process.env.NODE_ENV || "development") === "development",
  IS_PROD: process.env.NODE_ENV === "production",
} as const;

export const API_BASE = ENV.API_URL;

export default ENV;
