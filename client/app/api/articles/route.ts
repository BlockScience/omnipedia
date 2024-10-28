import { NextResponse } from "next/server";
import { parseWikicrow } from "@/lib/json";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const filePath = searchParams.get("path");

  if (!filePath) {
    return NextResponse.json(
      { error: "File path is required" },
      { status: 400 }
    );
  }

  const { data } = await parseWikicrow(filePath);

  if (data === null) {
    return NextResponse.json({ error: "File not found" }, { status: 404 });
  }

  return NextResponse.json({ data });
}
