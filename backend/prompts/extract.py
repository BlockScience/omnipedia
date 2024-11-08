import ell
from pydantic import BaseModel, Field, ValidationError
from typing import List, Dict
import json
import re


class Requirement(BaseModel):
    id: str = Field(description="Unique identifier in the format 'R{id}'")
    description: str = Field(description="Brief description of the requirement")
    reference: str = Field(description="Exact quote from the style guide")
    category: str = Field(description="Requirement type")
    classification: str = Field(description="Classification of the requirement")
    where: str = Field(description="Where the requirement should be applied")
    when: str = Field(description="When the requirement should be applied")


class Group(BaseModel):
    description: str = Field(description="Description of the group")
    category: str = Field(
        description="Category of the group (e.g., 'Language Usage', 'Formatting', etc.)"
    )
    requirements: List[Requirement] = Field(default_factory=list)


class RequirementsDocument(BaseModel):
    groups: List[Group] = Field(default_factory=list)

    def update(self, other: "RequirementsDocument") -> "RequirementsDocument":
        """Updates the current document with another, merging groups and requirements."""
        # Update logic for list-based groups
        existing_categories = {group.category for group in self.groups}

        for new_group in other.groups:
            if new_group.category not in existing_categories:
                # Add new group
                self.groups.append(new_group)
            else:
                # Update existing group
                existing_group = next(
                    g for g in self.groups if g.category == new_group.category
                )
                existing_req_ids = {req.id for req in existing_group.requirements}

                # Add new requirements
                for req in new_group.requirements:
                    if req.id not in existing_req_ids:
                        existing_group.requirements.append(req)

                # Update description if needed
                if new_group.description:
                    existing_group.description = new_group.description

        return self


# Define the ell function to extract requirements
@ell.simple(model="gpt-4o", temperature=0.0)
def extract_requirements_from_chunk(
    current_state: RequirementsDocument, chunk: str, i: int, total_chunks: int
):
    """Extract requirements from a chunk of the style guide."""
    return [
        ell.user(f"""Your task is to extract all requirements from a given style guide chunk and present them in a structured JSON format. Follow the steps below to ensure comprehensive and accurate extraction:

1. **Thoroughly Review the Style Guide Chunk**: Carefully read the provided chunk to understand its scope, target audience, and specific guidelines. TAKE YOUR TIME. 

2. **Identify Sections and Subsections**: Note any sections or subsections in the chunk to organize the extraction process.

3. **Extract ALL Prescriptive Guidelines**:
- **Locate Prescriptive Statements**: Find **ALL** statements that provide rules, guidelines, or recommended practices. Look for imperative language such as 'must', 'should', 'always', 'never', 'prefer', and 'avoid'.
- **Capture Exact Wording**: For each prescriptive statement, note the exact phrasing used in the style guide.

4. **Document Each Requirement in Detail**:
- **Unique Identifier**: Assign a unique ID to each requirement in the format "R{{id}}" (e.g., R1, R2, etc.).
- **Description**: Provide a concise summary of what the requirement entails.
- **Reference**: Include the exact quote from the style guide that defines the requirement.
- **Category**: Classify the requirement into a type such as "Content", "Formatting", "Language Usage", "Citations", "Infoboxes", or "Structure".

5. **Classify Each Requirement**:
- **Imperative Standards**: Non-negotiable requirements that must be included to ensure compliance.
- **Best Practices**: Strongly recommended guidelines that may be adjusted based on context.
- **Flexible Guidelines**: Optional guidelines that can be applied depending on the article's context.
- **Contextual Considerations**: Requirements that apply under specific conditions (e.g., certain article types or content).
- **Supplementary Information**: Additional, non-essential information that enhances the article.
- **Non-Applicable Elements**: Requirements that do not apply to the current article or content.

6. **Review Each Requirement**:
- **Where**: Determine where the requirement should be applied within an article (lead section, content section, infobox, etc.).
- **When**: Establish when the requirement should be applied, based on the article's specific content and context.

7. **Organize Requirements into Groups**: Categorize the requirements under relevant groups based on their nature (e.g., Content, Formatting).

8. **Format the Output as Structured JSON**:
- **Structure**: The JSON should have a top-level key named "groups", with each group containing:
    {{
        "description": "A brief description of what this group of requirements covers",
        "category": "The main category this group belongs to",
        "requirements": [array of requirement objects]
    }}
- **Requirement Object**: Each requirement should follow this structure:
    {{
        "id": "R{{id}}",
        "description": "Brief description of the requirement",
        "reference": "Exact quote from the style guide",
        "category": "Requirement type",
        "classification": "Classification of the requirement",
        "where": "Where the requirement should be applied",
        "when": "When the requirement should be applied"
    }}

9. **Ensure Completeness and Accuracy**: After extraction, review the JSON to confirm that all requirements from the style guide chunk are included and correctly categorized.

10. **Output Only the JSON**: The final response should contain only the JSON structure with all extracted requirements. Do not include any additional text or explanations.

Current State of Requirements Document:
{current_state.model_dump_json(indent=2)}

Chunk ({i}/{total_chunks}):
{chunk}

Do not include any explanations or text outside of the JSON output.
""")
    ]


# Function to split the text into manageable chunks
def split_content(requirements_text: str, max_chunk_size=2000) -> List[str]:
    """Split the style guide text into chunks not exceeding max_chunk_size."""
    paragraphs = re.split(r"\n\s*\n", requirements_text)
    chunks = []
    current_chunk = ""
    for para in paragraphs:
        if len(current_chunk) + len(para) + 2 <= max_chunk_size:
            current_chunk += para + "\n\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks


# Main function to process the text and extract requirements
def process_requirements(requirements_text: str) -> RequirementsDocument:
    ell.init(store="./logdir", autocommit=True, verbose=True)
    chunks = split_content(requirements_text)
    current_state = RequirementsDocument()
    total_chunks = len(chunks)
    for i, chunk in enumerate(chunks, start=1):
        # Extract requirements from the current chunk
        raw_output = extract_requirements_from_chunk(
            current_state, chunk, i, total_chunks
        )
        # Clean the output (remove any potential backticks)
        json_output = raw_output.replace("```json", "").replace("```", "").strip()
        try:
            # Parse the output into a RequirementsDocument
            new_requirements = RequirementsDocument.model_validate_json(json_output)
            # Update the current state with new requirements
            current_state.update(new_requirements)
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"Error parsing JSON in chunk {i}: {e}")
            print(f"Raw output:\n{json_output}\n")
        except Exception as e:
            print(f"Unexpected error in chunk {i}: {e}")
            print(f"Raw output:\n{json_output}\n")

    return current_state


# Example usage
if __name__ == "__main__":
    # Replace with your actual style guide content
    style_guide_content = """
[
  {
    "title": "Wikipedia:WikiProject Molecular Biology/Style guide (gene and protein articles)",
    "content": "",
    "hierarchy": "Wikipedia:WikiProject Molecular Biology/Style guide (gene and protein articles)"
  },
  {
    "title": "Introduction",
    "content": "<p>{{WikiProject style advice|WP:MCBMOS|MOS:MCB}}\nThis is a '''guideline''' for the structure of [[gene]] and [[protein]] articles on Wikipedia. It contains the articles naming conventions and the general recommended outline of an article, as well as useful information to bring an article to [[WP:GA|good article]] or [[WP:FA|featured article]] status.</p>\n",
    "hierarchy": "Introduction"
  },
  {
    "title": "General considerations",
    "content": "<p>The scope of a gene/protein article is the human gene/protein (including all splice variants derived from that gene) as well as [[Homology_(biology)#Orthology|orthologs]] (as listed in [[HomoloGene]]) that exist in other species. If there are [[Homology_(biology)#Paralogy|paralogs]] in humans (and by extension other species), then a gene family article in addition to the gene specific articles (see for example [[dopamine receptor]]) would be appropriate.</p>\n<p>In general, do not hype a study by listing the names, credentials, institutions, or other &quot;qualifications&quot; of their authors. Wikipedia is not a press release. Article prose should focus on what a cited study says about the structure, function, clinical significance, etc. of the gene or protein, not what the gene or protein says about a particular study or the research group who conducted that study. Particularly notable contributions along with who made the discovery however should be mentioned in the discovery/history [[Wikipedia:WikiProject_Molecular_and_Cellular_Biology/Style_guide_(gene_and_protein_articles)#Sections|section]].</p>\n",
    "hierarchy": "Introduction > General considerations"
  },
  {
    "title": "Article name",
    "content": "<p>If relatively short, the recommended [[UniProt]] protein name should be used as the article name. If the protein name is verbose, either a widely used protein acronym or the official [[Human Genome Organisation|HUGO]] gene symbol, followed by &quot;(gene)&quot; if necessary to disambiguate. UniProt names generally follow the [[IUBMB]] recommendations:</p>\n<p>{{talkquote|When naming proteins which can be grouped into a family based on homology or according to a notion of shared function (like the interleukins), the different members should be enumerated with a dash &quot;-&quot; followed by an Arabic number, e.g. &quot;desmoglein-1&quot;, &quot;desmoglein-2&quot;, etc.|source={{cite web | url = http://www.chem.qmul.ac.uk/iubmb/proteinName.html | title = Protein Naming Guidelines  | date = | work = Recommendations on Biochemical &amp; Organic Nomenclature, Symbols &amp; Terminology etc. | publisher = International Union of Biochemistry and Molecular Biology }} }}</p>\n<p>If the article is about a viral protein, it is recommended to include the taxon in the title, as &quot;nonstructual protein 2&quot; and &quot;viral protease&quot; can mean many things. A parenthesized term added to disambiguate common symbols does not constitute [[WP:PRIMARYREDIRECT|unnecessary disambiguation]] even when it is the only article with such a name.</p>\n",
    "hierarchy": "Introduction > Article name"
  },
  {
    "title": "Gene nomenclature",
    "content": "<p>{{See|Gene nomenclature}}</p>\n<p>The abbreviations of genes are according to [https://www.genenames.org/about/guidelines/ HUGO Gene Nomenclature Committee] and written in ''italic'' font style (the full names are also written in ''italic''). It is recommended that abbreviations instead of the full name are used. Human gene names are written in capitals, for example ''ALDOA'', ''INS'', etc. For orthologs of human genes in other species, only the initial letter is capitalised, for example mouse ''Aldoa'', bovine ''Ins'', etc.</p>\n<p>The following usages of gene symbols are recommended:</p>\n<ul>\n<li>&quot;the ALDOA gene is regulated...&quot;,</li>\n<li>&quot;the rat gene for Aldoa is regulated...&quot; or</li>\n<li>&quot;''ALDOA'' is regulated...&quot;,\nwhile the following is not recommended:</li>\n<li>&quot;the gene ''ALDOA'' is regulated&quot; since it is redundant.</li>\n</ul>\n",
    "hierarchy": "Introduction > Gene nomenclature"
  },
  {
    "title": "Images and diagrams",
    "content": "<p>{{See|Wikipedia:WikiProject Molecular and Cellular Biology/Diagram guide}}</p>\n<p>Where possible, diagrams should keep to a standard format. If the diagram guide does not give sufficient guidance on the style for the images in an article, consider suggesting expansions to the standardised formatting.</p>\n",
    "hierarchy": "Introduction > Images and diagrams"
  },
  {
    "title": "Infoboxes",
    "content": "<p>One or more of the following [[WP:INFOBOX|infoboxes]] as appropriate should be included at the top of each article:\n{| class=&quot;wikitable&quot;\n|-\n! width=&quot;100px&quot; | template\n! width=&quot;125px&quot; | description / suggested use\n! width=&quot;125px&quot; | example article containing this template\n! width=&quot;125px&quot; | template filling tool\n|-\n| align=&quot;center&quot; | {{tl|Infobox GNF protein}}\n| for genes/proteins for which an [[Homology_(biology)#Orthology|ortholog]] is present within the human genome (articles containing this template were created as part of the [[Gene Wiki]] project)\n| align=&quot;center&quot; | [[Reelin]]\n| align=&quot;center&quot; | [http://biogps.gnf.org/GeneWikiGenerator/#goto=welcome GeneWikiGenerator]&lt;br /&gt;(input: [[HUGO Gene Nomenclature Committee|HUGO gene symbol]])\n|-\n| align=&quot;center&quot; | {{tl|Infobox protein}}\n| smaller box appropriate for protein family articles where more than one protein is discussed in the same article (e.g., [[Homology_(biology)#Paralogy|paralogs]])\n| align=&quot;center&quot; | [[Estrogen receptor]]\n| align=&quot;center&quot; | [http://diberri.dyndns.org/cgi-bin/templatefiller/ Wikipedia template filling]&lt;br /&gt;(input: [[HUGO Gene Nomenclature Committee|HGNC ID]])\n|-\n| align=&quot;center&quot; | {{tl|Infobox nonhuman protein}}\n| for proteins without a human ortholog\n| align=&quot;center&quot; | [[Uterine serpin]]\n| align=&quot;center&quot; | —\n|-\n| align=&quot;center&quot; | {{tl|Infobox protein family}}\n| for protein families (evolutionary related proteins that share a common 3D structure) that are listed in [[Pfam]]\n| align=&quot;center&quot; | [[T-box]]\n| align=&quot;center&quot; | —\n|-\n| align=&quot;center&quot; | {{tl|Infobox rfam}}\n| for RNA families (evolutionary related non-coding RNAs that share a common 3D structure) that are listed in [[Rfam]]\n| align=&quot;center&quot; | [[U1 spliceosomal RNA]]\n| align=&quot;center&quot; | —\n|-\n| align=&quot;center&quot; | {{tl|Infobox enzyme}}\n| for enzymes based on [[Enzyme Commission number|EC number]] (more properly refers to the reaction catalyzed by the enzyme rather than the enzyme itself){{efn|It is very important to realize that EC describes the reaction, not a protein family. The editor should keep this distinction in mind, even when a source (often the IUBMB itself) describes an EC enzyme as belonging to a certain evolutionarily-defined family or using a certain mechanism. Checking Expacy or BioCyc for proteins to compare in InterPro may help.}}\n| align=&quot;center&quot; | [[Alcohol dehydrogenase]]\n| align=&quot;center&quot; | —\n|}</p>\n<p>If there is only one human paralog assigned to a given [[Enzyme Commission number|EC number]] (the [[ExPASy]] database maintains EC number to protein mappings), then in addition to a protein infobox, it may be appropriate to also add the corresponding enzyme infobox. Likewise, if there is only one human paralog that has been assigned to [[Pfam]] family, then including a protein family infobox may also be appropriate.</p>\n<p>There exist some cases where a large number of infoboxes may apply to an article. You may put less useful ones in a section at the end, laid side-by-side with a table. Collapsing or horizontally scrolling the said table is doubtful, as [[MOS:COLLAPSE]] may or may not apply depending on how &quot;extraneous&quot; the boxes are.</p>\n",
    "hierarchy": "Introduction > Infoboxes"
  },
  {
    "title": "Sections{{anchor|MCBMOSSECTIONS|Sections}}",
    "content": "<p>{{shortcut|WP:MCBMOSSECTIONS}}</p>\n",
    "hierarchy": "Introduction > Sections{{anchor|MCBMOSSECTIONS|Sections}}"
  },
  {
    "title": "'''Lead'''",
    "content": "<p>#: The [[WP:LEAD|lead section]] is defined as ''&quot;the section before the first headline. The table of contents, if displayed, appears between the lead section and the first headline.&quot;''\n#: The first sentence of the lead should define what the scope of the article is. For genes/proteins in which a human [[ortholog]] exists, &quot;'''&lt;recommended [[UniProt]] name&gt;''' is a [[protein]] that in humans is encoded by the ''&lt;approved [[Human Genome Organisation|HUGO]] gene symbol&gt;'' [[gene]].&quot; would be appropriate.</p>\n",
    "hierarchy": "'''Lead'''"
  },
  {
    "title": "'''Gene'''",
    "content": "<p>#: Specific information about the gene (on which human chromosome it is located, regulation, etc.). Much of this basic information may already contained in the infobox and should not be unnecessarily repeated in this section unless especially notable.</p>\n",
    "hierarchy": "'''Gene'''"
  },
  {
    "title": "'''Protein'''",
    "content": "<p>#: Specific information about the protein (splice variants, post translational modifications, etc.). Again, much of this basic information may already contained in the infobox and should not be unnecessarily repeated unless especially notable.</p>\n",
    "hierarchy": "'''Protein'''"
  },
  {
    "title": "'''Species, tissue, and subcellular distribution'''",
    "content": "<p>#: Optional section that concisely describes what species this gene is expressed (e.g., wide species distribution, bacteria, fungi, vertebrates, mammals, etc.), what tissue the protein is expressed, and which subcellular compartments or organelles the protein is found (excreted, cytoplasm, nucleus, mitochondria, cell membrane).</p>\n",
    "hierarchy": "'''Species, tissue, and subcellular distribution'''"
  },
  {
    "title": "'''Function'''",
    "content": "<p>#: Describe the function of the transcribed protein.</p>\n",
    "hierarchy": "'''Function'''"
  },
  {
    "title": "'''Interactions'''",
    "content": "<p>#: Optional section that lists proteins that the protein that is the subject of the article is known to [[protein-protein interaction|interact]] with.</p>\n",
    "hierarchy": "'''Interactions'''"
  },
  {
    "title": "'''Clinical significance'''",
    "content": "<p>#: List diseases or conditions that are a result of a mutation in the gene or a deficiency or excess of the expressed protein.</p>\n",
    "hierarchy": "'''Clinical significance'''"
  },
  {
    "title": "'''History/Discovery'''",
    "content": "<p>#: In general, it is not appropriate to mention the research group or institution that conducted a study directly in the text of the article. However it is appropriate to list the names of those who made key discoveries concerning the gene or protein in this section (e.g., the scientist or group that originally cloned the gene, determined its function, linked it to a disease, won a major award for the discovery, etc.).</p>\n<p>Example articles of what such an organization may look like are: [[Protein C]], [[Gonadotropin-releasing hormone]] or [[Rubisco]].</p>\n",
    "hierarchy": "'''History/Discovery'''"
  },
  {
    "title": "Wikidata item",
    "content": "<p>The Wikipedia article should be linked to a Wikidata item of the entity first mentioned in the first sentence of the lead section, which should be written as defined in [[WP:MCBMOSSECTIONS]]. Suppose that the first sentence is &quot;'''Steroid 21-hydroxylase''' is a [[protein]] that in humans is encoded by the ''CYP21A2 '' [[gene]].&quot; In this case, the Wikipedia article should be linked to a Wikidata item of the steroid 21-hydroxylase protein rather than the gene.</p>\n",
    "hierarchy": "'''History/Discovery''' > Wikidata item"
  },
  {
    "title": "Citing sources",
    "content": "<p>''For guidance on choosing and using reliable sources, see [[Wikipedia:Identifying reliable sources (natural sciences)]] and [[Wikipedia:Reliable sources#Physical sciences, mathematics and medicine|Wikipedia:Reliable sources]].''</p>\n<p>''For general guidance on citing sources see [[Wikipedia:Citing sources]], [[Wikipedia:Footnotes]] and [[Wikipedia:Guide_to_layout#standard_appendices|Wikipedia:Guide to layout]].''</p>\n<p>MCB articles should be relatively dense with inline citations, using either [[H:FOOT|&lt;nowiki&gt;&lt;ref&gt;&lt;/nowiki&gt; tags (footnotes)]] or [[WP:PAREN|parenthetical citations]]. It is not acceptable to write substantial amounts of prose and then add your textbook to the ''References'' section as a [[WP:CITE#General_reference|non-specific or general reference]]. It is too easy for a later editor to change the body text and then nobody is sure which statements are backed up by which sources.</p>\n<p>There is no standard for formatting citations on Wikipedia, but the format should be consistent within any one article. Some editors format their citations by hand, which gives them control over the presentation. Others prefer to use [[WP:CITET|citation templates]] such as {{Tlx|Cite journal}}, {{Tlx|Cite book}}, {{Tlx|Cite web}}, {{Tlx|Cite press release}} and {{Tlx|Cite news}}. Citations in the [[Vancouver system|Vancouver format]] can be produced using the {{para|vauthors}} or {{para|veditors}} parameters. The ''[[Uniform Requirements for Manuscripts Submitted to Biomedical Journals]]'' (URM) citation guidelines list up to six authors, followed by ''et al.'' if there are more than six.&lt;ref name=URM&gt;{{cite web|url=http://www.nlm.nih.gov/bsd/uniform_requirements.html |title=International Committee of Medical Journal Editors (ICMJE) Uniform Requirements for Manuscripts Submitted to Biomedical Journals: Sample References|publisher=United States [[National Library of Medicine]] |work=MEDLINE/Pubmed Resources|accessdate=2009-10-08}}&lt;/ref&gt; Some editors prefer to expand the abbreviated journal name; others prefer concise standard abbreviations.</p>\n<p>Abstracts of most MCB related journals are [[Gratis versus libre|freely available]] at [[PubMed]], which includes a means of searching the [[MEDLINE]] database. The easiest way to populate the journal and book citation templates is to use [[User:Diberri|Diberri]]'s template-filling web site or the [[WP:URF|Universal reference formatter]]. Search [https://www.ncbi.nlm.nih.gov/pubmed PubMed] for your journal article and enter the [[PMID]] (PubMed Identifier) into [https://tools.wmflabs.org/citation-template-filling/cgi-bin/index.cgi Diberri's template filler] or the [http://toolserver.org/~verisimilus/Scholar/Cite.php Universal reference formatter]{{dead link}}. If you use [[Internet Explorer]] or [[Mozilla Firefox]] (2.0+), then [[User:Wouterstomp/Bookmarklet|Wouterstomp's bookmarklet]] can automate this step from the PubMed abstract page. Take care to check that all the fields are correctly populated, since the tool does not always work 100%. For books, enter the ISBN into [https://tools.wmflabs.org/citation-template-filling/cgi-bin/index.cgi Diberri's tool]. Multiple references to the same source citation can be achieved by ensuring the inline reference is named uniquely. Diberri's tool can format a reference with the PMID or ISBN as the name.</p>\n<p>In addition to the standard citation text, it is useful to supply hyperlinks. If the journal abstract is available on PubMed, add a link by typing &lt;code&gt;[[Wikipedia:PMID|PMID]] xxxxxxxxx&lt;/code&gt;. If the article has a [[digital object identifier]] (DOI), use the {{tl|doi}} template. If and only if the article's full text is freely available online, supply a [[uniform resource locator]] (URL) to this text by hyperlinking the article title in the citation. If the full text is freely available on the journal's website and on PubMed Central, prefer to link the former as PubMed central's copy is often a pre-publication draft. When the source text is available in both [[HTML]] and [[PDF]], the former should be preferred as it is compatible with a larger range of browsers. If citation templates are used, these links can be supplied via the {{para|pmid}}, {{para|doi}}, {{para|url}} and {{para|pmc}} parameters. Do not add a &quot;Retrieved on&quot; date for [[Wikipedia:convenience links|convenience links]] to online editions of paper journals (however &quot;Retrieved on&quot; dates are needed on other websources).</p>\n<p>For example:\n{{Automarkup|{{Make code|1=Levy R, Cooper P. [http://www.mrw.interscience.wiley.com/cochrane/clsysrev/articles/CD001903/frame.html Ketogenic diet for epilepsy.] Cochrane Database Syst Rev. 2003;(3):CD001903. &lt;&lt;doi!10.1002/14651858.CD001903&gt;&gt;. &lt;&lt;PMID!12917915&gt;&gt;.}}}}</p>\n<p>A citation using {{tl|cite journal}}:</p>\n<p>{{Automarkup|{{Make code|1=&lt;&lt;cite journal !vauthors=Bannen RM, Suresh V, Phillips GN Jr, Wright SJ, Mitchell JC !title=Optimal design of thermally stable proteins !journal=Bioinformatics !volume=24 !issue=20 !pages=2339–43 !year=2008 !pmid=18723523 !pmc=2562006 !doi=10.1093/bioinformatics/btn450 !url=http://bioinformatics.oxfordjournals.org/cgi/content/full/24/20/2339&gt;&gt;}}}}</p>\n<p>Or the alternative {{tl|vcite journal}}:</p>\n<p>{{Automarkup|{{Make code|1=&lt;&lt;vcite journal !author=Bannen RM, Suresh V, Phillips GN Jr, Wright SJ, Mitchell JC !title=Optimal design of thermally stable proteins !journal=Bioinformatics !volume=24 !issue=20 !pages=2339–43 !year=2008 !pmid=18723523 !pmc=2562006 !doi=10.1093/bioinformatics/btn450 !url=http://bioinformatics.oxfordjournals.org/cgi/content/full/24/20/2339&gt;&gt;}}}}</p>\n<p>&lt;br /&gt;{{reflist talk|closed=1}}</p>\n",
    "hierarchy": "'''History/Discovery''' > Citing sources"
  },
  {
    "title": "Navigation box",
    "content": "<p>Articles about related proteins may be cross linked by including one or more [[WP:NAVBOX|navigation boxes]] as appropriate. Examples include:</p>\n<ul>\n<li>{{tl|Cytoskeletal Proteins}}</li>\n<li>{{tl|Ion channels}}</li>\n<li>{{tl|Transcription factors}}</li>\n<li>{{tl|Transmembrane receptors}}</li>\n</ul>\n",
    "hierarchy": "'''History/Discovery''' > Navigation box"
  },
  {
    "title": "Categories",
    "content": "<p>Every Wikipedia article should be added to at least one [[WP:CATEGORY|category]]. Categories or subcategories that may be appropriate for gene and protein articles include:</p>\n<ul>\n<li>[[:Category:Proteins]]</li>\n<li>[[:Category:Enzymes by function]]</li>\n<li>[[:Category:Genes by human chromosome]]</li>\n</ul>\n",
    "hierarchy": "'''History/Discovery''' > Categories"
  },
  {
    "title": "Notes",
    "content": "<p>{{notelist}}</p>\n<p>[[Category:WikiProject style advice|Style guide]]</p>\n",
    "hierarchy": "'''History/Discovery''' > Notes"
  }
]
    """
    # Process the style guide to extract requirements
    requirements_document = process_requirements(style_guide_content)
    # Output the final JSON
    with open("requirements.json", "w", encoding="utf-8") as f:
        json.dump(requirements_document.model_dump(), f, indent=4)

    print(json.dumps(requirements_document.model_dump(), indent=4))
