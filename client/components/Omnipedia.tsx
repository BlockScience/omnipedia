"use client";

import React, { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ChevronDown, ChevronUp, ClipboardCheck, Link2 } from "lucide-react";
import { SectionFeedback } from "@/components/SectionFeedback";
import { RequirementsSidebar } from "@/components/RequirementsSidebar";
import { requirementsData } from "@/lib/data";
import { GenerateCitations } from "./GenerateCitations";
import useSWR from "swr";
import { ArticleSelector } from "./ArticleSelector";
import {
  ArticleSection,
  SectionState,
  CategoryScore,
  Feedback,
  RequirementClassification,
  RequirementEvaluation,
} from "@/lib/types";
import { ContentRenderer } from "./ContentRenderer";
import { Badge } from "./ui/badge";

interface SelectedRequirement {
  id: string;
  category: string;
}

interface FilterHistoryEntry {
  searchQuery: string;
  classification: RequirementClassification | null;
  lastUsed: Date;
}

const MainContent = () => {
  // Core state
  const [selectedPath, setSelectedPath] = useState("");
  const [article, setArticle] = useState<ArticleSection[]>([]);
  const [evaluation, setEvaluation] = useState<ArticleSection[]>([]);
  const [selectedSection, setSelectedSection] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<Feedback>();
  console.log("SELECTED: ", selectedSection);
  // Enhanced state
  const [selectedRequirements, setSelectedRequirements] = useState<
    SelectedRequirement[]
  >([]);
  const [sectionStates, setSectionStates] = useState<
    Record<string, SectionState>
  >({});
  const [categoryScores, setCategoryScores] = useState<
    Record<string, CategoryScore>
  >({});
  const [filterHistory, setFilterHistory] = useState<FilterHistoryEntry[]>([]);

  const fetcher = (url: string) => fetch(url).then((res) => res.json());

  const { data: evaluationData, error: evaluationError } = useSWR(
    selectedPath
      ? `/api/evaluation?path=${encodeURIComponent(selectedPath)}`
      : null,
    fetcher,
    { revalidateOnFocus: false, revalidateOnReconnect: false }
  );

  const { data: articleData, error: articleError } = useSWR(
    selectedPath
      ? `/api/articles?path=${encodeURIComponent(selectedPath)}`
      : null,
    fetcher,
    { revalidateOnFocus: false, revalidateOnReconnect: false }
  );

  // Section state management
  const toggleSection = (title: string) => {
    setSectionStates((prev) => ({
      ...prev,
      [title]: {
        isExpanded: !prev[title]?.isExpanded,
        lastViewed: new Date(),
        scores: prev[title]?.scores || {},
      },
    }));
    setSelectedSection((prev) => (prev === title ? null : title));
  };

  // Requirement selection management
  const toggleRequirement = (id: string, category: string) => {
    setSelectedRequirements((prev) => {
      const exists = prev.find((req) => req.id === id);
      if (exists) {
        return prev.filter((req) => req.id !== id);
      }
      return [...prev, { id, category }];
    });
  };

  // Score management with caching
  const updateCategoryScore = (
    category: string,
    evaluations: RequirementEvaluation[]
  ) => {
    const currentTime = new Date();
    const cached = categoryScores[category];

    if (
      cached &&
      currentTime.getTime() - cached.lastCalculated.getTime() < 5000
    ) {
      return cached.score;
    }

    const score =
      evaluations.reduce((acc, evaluation) => acc + evaluation.score, 0) /
      evaluations.length;

    setCategoryScores((prev) => ({
      ...prev,
      [category]: {
        score,
        lastCalculated: currentTime,
        evaluations,
      },
    }));

    return score;
  };

  // Data initialization and updates
  useEffect(() => {
    if (evaluationData?.data) {
      // Add the optional chaining here
      const { data } = evaluationData;
      console.log("EVALUATION DATA: ", data);
      setEvaluation(data);

      // Initialize or update section states
      const newSectionStates: Record<string, SectionState> = {};
      data.forEach((section: ArticleSection) => {
        newSectionStates[section.title] = {
          isExpanded: sectionStates[section.title]?.isExpanded || false,
          lastViewed: new Date(),
          scores: sectionStates[section.title]?.scores || {},
        };
      });
      setSectionStates(newSectionStates);
    }
  }, [evaluationData]);

  useEffect(() => {
    if (articleData?.data) {
      // Add the same check here for consistency
      const { data } = articleData;
      setArticle(data);
    }
  }, [articleData]);

  useEffect(() => {
    if (articleData) {
      const { data } = articleData;
      setArticle(data);
    }
  }, [articleData]);

  // Feedback updates
  useEffect(() => {
    if (selectedSection && evaluation) {
      const section = evaluation.find(
        (item) => item?.title === selectedSection
      );
      if (section) {
        setFeedback(section.feedback);
      }
    }
  }, [selectedSection, evaluation]);

  const handleArticleSelect = (source: string, acronym: string) => {
    const newPath = `${source}/${acronym}`;
    setSelectedPath(newPath);
    // Preserve states but clear current section
    setSelectedSection(null);
    setFeedback(undefined);
  };

  const handleFilterChange = (
    searchQuery: string,
    classification: RequirementClassification | null
  ) => {
    setFilterHistory((prev) => [
      {
        searchQuery,
        classification,
        lastUsed: new Date(),
      },
      ...prev.slice(0, 9), // Keep last 10 filters
    ]);
  };

  if (selectedPath && (!articleData || !evaluationData)) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <span className="loading loading-spinner"></span>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (articleError || evaluationError) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center text-red-500">
          <p>Error loading data</p>
        </div>
      </div>
    );
  }

  return (
    <ScrollArea className="h-auto w-full max-w-6xl mx-auto p-4 overflow-hidden">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-3xl">
              {(article && article[0]?.title) || "Select an Article"}
            </CardTitle>
            <ArticleSelector onSelect={handleArticleSelect} />
          </div>
        </CardHeader>
      </Card>

      {article &&
        article.map((section, index) => {
          const hasEvaluation = evaluation?.find(
            (e) => e.title === section.title
          )?.feedback;
          console.log("HAS EVAL: ", hasEvaluation);
          console.log("TITLE: ", section.title);
          const evaluationCount = hasEvaluation
            ? Object.values(hasEvaluation).reduce(
                (acc, category) =>
                  acc +
                  category.reduce(
                    (sum, section) =>
                      sum + section.requirement_evaluations.length,
                    0
                  ),
                0
              )
            : 0;

          return section.content !== "" ||
            (section.citations && section.citations.length > 0) ? (
            <Card
              key={index}
              className={`mb-2 ${
                selectedRequirements.some((req) =>
                  section.content.toLowerCase().includes(req.id.toLowerCase())
                )
                  ? "ring-2 ring-blue-500"
                  : ""
              }`}
            >
              <CardHeader
                className="flex flex-row items-center justify-between cursor-pointer"
                onClick={() => toggleSection(section.title)}
              >
                <CardTitle>{section.title}</CardTitle>
                <div className="flex items-center gap-3">
                  {section.citations && section.citations.length > 0 && (
                    <Badge
                      variant="outline"
                      className="flex items-center gap-1"
                    >
                      <Link2 className="h-3 w-3" />
                      {section.citations.length}
                    </Badge>
                  )}
                  {hasEvaluation && (
                    <Badge
                      variant="secondary"
                      className="flex items-center gap-1"
                    >
                      <ClipboardCheck className="h-3 w-3" />
                      {evaluationCount} evaluations
                    </Badge>
                  )}
                  {sectionStates[section.title]?.isExpanded ? (
                    <ChevronUp className="h-6 w-6" />
                  ) : (
                    <ChevronDown className="h-6 w-6" />
                  )}
                </div>
              </CardHeader>
              <CardContent className="pb-0">
                <div>
                  {section.content && section.content.trim() !== "" && (
                    <ContentRenderer content={section.content} />
                  )}
                  {section.citations && section.citations.length > 0 && (
                    <GenerateCitations citationsArray={section.citations} />
                  )}
                </div>
                {selectedSection === section.title && feedback && (
                  <SectionFeedback
                    feedback={feedback}
                    sectionState={sectionStates[section.title]}
                    selectedRequirements={
                      new Set(selectedRequirements.map((r) => r.id))
                    }
                    onRequirementSelect={toggleRequirement}
                    onScoreUpdate={(category, score) => {
                      setSectionStates((prev) => ({
                        ...prev,
                        [section.title]: {
                          ...prev[section.title],
                          scores: {
                            ...prev[section.title].scores,
                            [category]: score,
                          },
                        },
                      }));
                    }}
                  />
                )}
              </CardContent>
            </Card>
          ) : null;
        })}
    </ScrollArea>
  );
};

export const Omnipedia = () => {
  return (
    <div className="flex h-screen">
      <RequirementsSidebar groups={requirementsData.groups} />
      <main className="flex-1 overflow-auto mt-8">
        <MainContent />
      </main>
    </div>
  );
};
