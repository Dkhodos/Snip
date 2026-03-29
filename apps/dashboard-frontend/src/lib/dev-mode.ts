const CLERK_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

export const DEV_MODE = !CLERK_KEY || CLERK_KEY === "pk_test_...";
