import React, { useState, useMemo } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "@/components/ui/hover-card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Search, MapPin, Clock, Info } from "lucide-react";

// Classification types
export type RequirementClassification =
  | "Imperative Standards"
  | "Best Practices"
  | "Flexible Guidelines"
  | "Contextual Considerations";

// Single requirement
export interface Requirement {
  id: string;
  description: string;
  reference?: string;
  classification: RequirementClassification;
  where: string;
  when: string;
}

// Group of requirements
export interface RequirementGroup {
  description: string;
  requirements: Requirement[];
}

// Full requirements index
export interface RequirementsIndex {
  groups: {
    [key: string]: RequirementGroup;
  };
}

// Props for the sidebar component
export interface RequirementsSidebarProps {
  groups: RequirementsIndex["groups"];
}

// Props for the requirement component
export interface RequirementProps {
  requirement: Requirement;
}

// Classification badge variants
const getClassificationBadge = (classification: string) => {
  switch (classification) {
    case "Imperative Standards":
      return <Badge variant="destructive">Imperative</Badge>;
    case "Best Practices":
      return <Badge variant="secondary">Best Practice</Badge>;
    case "Flexible Guidelines":
      return <Badge variant="outline">Flexible</Badge>;
    case "Contextual Considerations":
      return <Badge>Contextual</Badge>;
    default:
      return <Badge variant="outline">{classification}</Badge>;
  }
};

const Requirement = ({ requirement }: RequirementProps) => (
  <HoverCard>
    <HoverCardTrigger asChild>
      <div className="flex items-center gap-2 p-2 rounded hover:bg-gray-100 cursor-pointer group">
        <div className="w-8 text-sm font-medium text-gray-500">
          {requirement.id}
        </div>
        <div className="flex-1 text-sm group-hover:text-gray-900">
          {requirement.description}
        </div>
        {getClassificationBadge(requirement.classification)}
      </div>
    </HoverCardTrigger>
    <HoverCardContent className="w-80">
      <div className="space-y-3">
        <div>
          <h4 className="font-medium flex items-center gap-2">
            {requirement.id}
            {getClassificationBadge(requirement.classification)}
          </h4>
          <p className="text-sm text-gray-600 mt-1">
            {requirement.description}
          </p>
        </div>

        <Separator />

        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm">
            <MapPin className="h-4 w-4 text-gray-500" />
            <span>{requirement.where}</span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <Clock className="h-4 w-4 text-gray-500" />
            <span>{requirement.when}</span>
          </div>
        </div>

        {requirement.reference && (
          <div className="pt-2">
            <p className="text-xs text-gray-500 italic">
              "{requirement.reference}"
            </p>
          </div>
        )}
      </div>
    </HoverCardContent>
  </HoverCard>
);

export const RequirementsSidebar = ({ groups }: RequirementsSidebarProps) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedClassification, setSelectedClassification] = useState<
    string | null
  >(null);

  // Search function
  const filteredGroups = useMemo<RequirementsIndex["groups"]>(() => {
    const searchLower = searchQuery.toLowerCase();

    return Object.entries(groups).reduce<RequirementsIndex["groups"]>(
      (acc, [groupName, group]) => {
        const filteredRequirements = group.requirements.filter((req) => {
          // Filter by classification if selected
          if (
            selectedClassification &&
            req.classification !== selectedClassification
          ) {
            return false;
          }

          // Search across all fields
          return (
            req.id.toLowerCase().includes(searchLower) ||
            req.description.toLowerCase().includes(searchLower) ||
            req.where.toLowerCase().includes(searchLower) ||
            req.when.toLowerCase().includes(searchLower) ||
            (req.reference &&
              req.reference.toLowerCase().includes(searchLower)) ||
            req.classification.toLowerCase().includes(searchLower)
          );
        });

        if (filteredRequirements.length > 0) {
          acc[groupName] = {
            ...group,
            requirements: filteredRequirements,
          };
        }

        return acc;
      },
      {}
    );
  }, [groups, searchQuery, selectedClassification]);
  const classifications = useMemo(
    () =>
      Array.from(
        new Set(
          Object.values(groups)
            .flatMap((group) => group.requirements)
            .map((req) => req.classification)
        )
      ),
    [groups]
  );

  return (
    <div className="w-80 h-screen border-r bg-gray-50 flex flex-col">
      {/* Info Header */}
      <div className="p-4 bg-white border-b">
        <Alert>
          <Info className="h-4 w-4" />
          <AlertTitle>Requirements Index</AlertTitle>
          <AlertDescription className="text-xs text-gray-600">
            Browse and search content requirements by category, classification,
            or keyword.
          </AlertDescription>
        </Alert>
      </div>

      {/* Search and Filters */}
      <div className="p-4 border-b bg-white space-y-4">
        <div className="relative">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-gray-500" />
          <Input
            placeholder="Search requirements..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-8"
          />
        </div>

        <div className="flex flex-wrap gap-2">
          <Button
            variant={!selectedClassification ? "secondary" : "outline"}
            size="sm"
            onClick={() => setSelectedClassification(null)}
          >
            All
          </Button>
          {classifications.map((classification) => (
            <Button
              key={classification}
              variant={
                selectedClassification === classification
                  ? "secondary"
                  : "outline"
              }
              size="sm"
              onClick={() => setSelectedClassification(classification)}
            >
              {classification.split(" ")[0]}
            </Button>
          ))}
        </div>
      </div>

      {/* Requirements List */}
      <ScrollArea className="flex-1">
        <div className="p-4">
          <Accordion type="multiple" className="space-y-2">
            {Object.entries(filteredGroups).map(([groupName, group]) => (
              <AccordionItem key={groupName} value={groupName}>
                <AccordionTrigger className="hover:no-underline">
                  <div className="flex items-center gap-2">
                    <span>{groupName}</span>
                    <Badge variant="secondary">
                      {group.requirements.length}
                    </Badge>
                  </div>
                </AccordionTrigger>
                <AccordionContent>
                  <div className="px-2 pt-2 text-xs text-gray-500">
                    {group.description}
                  </div>
                  <div className="mt-2">
                    {group.requirements.map((req) => (
                      <Requirement key={req.id} requirement={req} />
                    ))}
                  </div>
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>
      </ScrollArea>

      {/* Stats Footer */}
      <div className="p-4 border-t bg-white">
        <div className="flex justify-between text-sm text-gray-600">
          <span>
            {Object.values(filteredGroups).reduce(
              (acc, group) => acc + group.requirements.length,
              0
            )}{" "}
            requirements
          </span>
          <span>{Object.keys(filteredGroups).length} groups</span>
        </div>
      </div>
    </div>
  );
};
