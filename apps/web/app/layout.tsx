import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "Consulting Intelligence",
  description: "Evidence-first consulting investigations"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
