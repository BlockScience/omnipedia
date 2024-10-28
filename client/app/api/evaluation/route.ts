import { NextResponse } from "next/server";
import { getData } from "@/lib/json";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const filePath = searchParams.get("path");

  if (!filePath) {
    return NextResponse.json(
      { error: "File path is required" },
      { status: 400 }
    );
  }

  const { data } = await getData(filePath);

  if (data === null) {
    return NextResponse.json({ error: "File not found" }, { status: 404 });
  }

  return NextResponse.json({ data });
}
