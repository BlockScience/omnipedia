import React from "react";
import useSWR from "swr";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { ChevronDown } from "lucide-react";

export const ArticleSelector = ({
  onSelect,
}: {
  onSelect: (source: string, acronym: string) => void;
}) => {
  const acronyms = ["ADCYAP1", "AGK", "ATF1", "ABCC11", "ANLN"];
  const sources = ["wikipedia", "wikicrow"];

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className="w-[200px] justify-between">
          Select Article
          <ChevronDown className="ml-2 h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>

      <DropdownMenuContent className="w-[200px]">
        {sources.map((source) => (
          <DropdownMenuSub key={source}>
            <DropdownMenuSubTrigger className="capitalize">
              {source}
            </DropdownMenuSubTrigger>
            <DropdownMenuSubContent>
              {acronyms.map((acronym) => (
                <DropdownMenuItem
                  key={`${source}-${acronym}`}
                  onClick={() => onSelect(source, acronym)}
                >
                  {acronym}
                </DropdownMenuItem>
              ))}
            </DropdownMenuSubContent>
          </DropdownMenuSub>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
