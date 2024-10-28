import React from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { AlertCircle, CheckCircle, Info, HelpCircle } from "lucide-react";
import { requirementsData } from "@/lib/data";
import {
  CategoryScore,
  Feedback,
  RequirementEvaluation,
  SectionState,
} from "@/lib/types";

interface SectionFeedbackProps {
  feedback: Feedback;
  sectionState: SectionState;
  onRequirementSelect: (requirementId: string, category: string) => void;
  selectedRequirements: Set<string>;
  onScoreUpdate: (category: string, score: CategoryScore) => void;
}

export const SectionFeedback: React.FC<SectionFeedbackProps> = ({
  feedback,
  sectionState,
  onRequirementSelect,
  selectedRequirements,
  onScoreUpdate,
}) => {
  const calculateCategoryScore = (
    category: string,
    evaluations: RequirementEvaluation[]
  ) => {
    // Check if we have a cached score that's less than 5 seconds old
    const cachedScore = sectionState.scores[category];
    if (
      cachedScore &&
      new Date().getTime() - cachedScore.lastCalculated.getTime() < 5000
    ) {
      return cachedScore.score;
    }

    // Calculate new score
    if (!evaluations.length) return 0;
    const scores = evaluations.map((req) => req.score);
    const average = scores.reduce((acc, curr) => acc + curr, 0) / scores.length;

    // Cache the new score
    const newScore = {
      score: average,
      lastCalculated: new Date(),
      evaluations,
    };
    onScoreUpdate(category, newScore);

    return average;
  };

  const getScoreBadgeVariant = (score: number) => {
    if (score >= 0.8) return "secondary";
    if (score >= 0.6) return "outline";
    return "destructive";
  };

  if (!feedback) return null;

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          Section Feedback
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger>
                <HelpCircle className="h-5 w-5 text-gray-400" />
              </TooltipTrigger>
              <TooltipContent>
                <p>Detailed feedback for each category and requirement</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </CardTitle>
        <CardDescription>
          Analysis of content requirements and guidelines
        </CardDescription>
      </CardHeader>

      <CardContent className="mb-0">
        <Tabs defaultValue="infoboxes" className="w-full">
          <TabsList className="w-full">
            {Object.entries(feedback)
              .sort(([a], [b]) => a.localeCompare(b))
              .map(([category, categoryData]) => {
                const evaluationCount = categoryData.reduce(
                  (acc, section) =>
                    acc + section.requirement_evaluations.length,
                  0
                );

                return (
                  <TabsTrigger
                    key={category}
                    value={category.toLowerCase()}
                    className="flex items-center gap-2"
                  >
                    {category}
                    <Badge
                      variant="secondary"
                      className="h-5 w-5 flex items-center justify-center rounded-full"
                    >
                      {evaluationCount}
                    </Badge>
                  </TabsTrigger>
                );
              })}
          </TabsList>

          {Object.entries(feedback).map(([category, categoryData]) => (
            <TabsContent key={category} value={category.toLowerCase()}>
              <ScrollArea className="h-[calc(100vh-300px)] min-h-[400px] max-h-[600px] pr-4">
                {categoryData.map((section, sectionIndex) => (
                  <div key={sectionIndex} className="mb-6">
                    {section.meta_notes && (
                      <Alert className="mb-4">
                        <Info className="h-4 w-4" />
                        <AlertTitle>Meta Notes</AlertTitle>
                        <AlertDescription>
                          {section.meta_notes}
                        </AlertDescription>
                      </Alert>
                    )}

                    {section.requirement_evaluations.length > 0 && (
                      <div className="mb-4">
                        <Alert>
                          <AlertCircle className="h-4 w-4" />
                          <AlertTitle>Category Score</AlertTitle>
                          <AlertDescription className="mt-2">
                            <Progress
                              value={
                                calculateCategoryScore(
                                  category,
                                  section.requirement_evaluations
                                ) * 100
                              }
                              className="h-2"
                            />
                            <span className="text-sm text-gray-500 mt-1 block">
                              {(
                                calculateCategoryScore(
                                  category,
                                  section.requirement_evaluations
                                ) * 100
                              ).toFixed(1)}
                              % compliance
                            </span>
                          </AlertDescription>
                        </Alert>
                      </div>
                    )}

                    <Accordion type="single" collapsible className="w-full">
                      {section.requirement_evaluations.map((req, index) => (
                        <AccordionItem
                          key={index}
                          value={`item-${index}`}
                          className={
                            selectedRequirements.has(req.requirement_id)
                              ? "ring-2 ring-blue-500"
                              : ""
                          }
                          onClick={() =>
                            onRequirementSelect(req.requirement_id, category)
                          }
                        >
                          <AccordionTrigger className="hover:no-underline">
                            <div className="flex items-center gap-2">
                              {req.score === 1.0 ? (
                                <CheckCircle className="h-4 w-4 text-green-500" />
                              ) : req.score === 0.0 ? (
                                <AlertCircle className="h-4 w-4 text-red-500" />
                              ) : (
                                <Info className="h-4 w-4 text-yellow-500" />
                              )}
                              <span>Requirement {req.requirement_id}</span>
                              <Badge variant={getScoreBadgeVariant(req.score)}>
                                {(req.score * 100).toFixed(0)}%
                              </Badge>
                              <Badge variant="outline">
                                Confidence: {(req.confidence * 100).toFixed(0)}%
                              </Badge>
                            </div>
                          </AccordionTrigger>
                          <AccordionContent>
                            <div className="space-y-4 p-4">
                              <div className="space-y-2">
                                <h4 className="font-medium">Applicability</h4>
                                <p className="text-sm text-gray-600">
                                  {req.applicability_reasoning}
                                </p>
                              </div>

                              <div className="space-y-2">
                                <h4 className="font-medium">Evidence</h4>
                                <p className="text-sm text-gray-600">
                                  {req.evidence}
                                </p>
                              </div>

                              <div className="space-y-2">
                                <h4 className="font-medium">Reasoning</h4>
                                <p className="text-sm text-gray-600">
                                  {req.reasoning}
                                </p>
                              </div>

                              {req.overlap_notes &&
                                req.overlap_notes !== "N/A" && (
                                  <div className="space-y-2">
                                    <h4 className="font-medium">
                                      Overlap Notes
                                    </h4>
                                    <p className="text-sm text-gray-600">
                                      {req.overlap_notes}
                                    </p>
                                  </div>
                                )}
                            </div>
                          </AccordionContent>
                        </AccordionItem>
                      ))}
                    </Accordion>
                  </div>
                ))}
              </ScrollArea>
            </TabsContent>
          ))}
        </Tabs>
      </CardContent>
    </Card>
  );
};
