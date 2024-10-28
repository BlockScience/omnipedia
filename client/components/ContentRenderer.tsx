import React from "react";
import parse from "html-parse-string";

export const ContentRenderer = ({ content }: { content: string }) => {
  // Remove extra spaces and newlines between tags
  const cleanContent = content
    .replace(/>\s+</g, "><")
    .replace(/\s+/g, " ")
    .trim();

  // Safely render the HTML content
  const createMarkup = () => ({ __html: cleanContent });

  return (
    <div className="text-gray-700" dangerouslySetInnerHTML={createMarkup()} />
  );
};
