export const site = {
  name: 'Layne Intellectual Property',
  origin: 'https://layne-intellectual-property.robertmlayne.chatgpt.site',
  email: 'robert@layneip.com', phone: '+1 (571) 274-0684', telephone: '+15712740684',
  professional: 'Robert M. Layne, Ph.D.', registration: '82,283',
  location: 'Pittsburgh region, Pennsylvania', updated: '2026-09-21',
  publicationMode: 'private-review',
};

export const services = [
  {
    slug: 'patent-preparation', name: 'Patent preparation', group: 'Protect',
    short: 'Translate a complex invention into a clear specification, drawings, and a considered claim structure.',
    lead: 'Start with the invention. Build the application around what makes it different.',
    paragraphs: [
      'A useful patent application begins with a precise account of the technical problem, the proposed solution, and the variations that matter. Invention interviews connect the inventor’s understanding with a written disclosure that can support examination and future claim development.',
      'Preparation can encompass U.S. provisional and nonprovisional utility applications, supporting figures, coordinated inventor review, and a documented drafting process. The scope is selected around the maturity of the technology, the available disclosure, and the intended filing strategy.'
    ],
    includes: ['Invention interviews and disclosure review', 'Technical decomposition and claim architecture', 'Specification and claim drafting', 'Figure planning and drawing coordination', 'Review of alternative embodiments and implementation details', 'Inventor review and filing-package preparation'],
    deliverables: ['Application draft with an organized review trail', 'Claim-to-disclosure support map', 'Open questions and filing-readiness checklist'],
    fit: 'Inventors, founders, research teams, and patent counsel preparing an initial filing or a new application.',
    scope: 'A provisional application is a filing option, not an issued patent. The appropriate application and priority strategy depend on the actual disclosure and circumstances.',
    related: ['office-action-responses', 'continuations-portfolio', 'prior-art'],
    sources: [['USPTO: applying for a patent', 'https://www.uspto.gov/patents/basics/apply'], ['USPTO: provisional applications', 'https://www.uspto.gov/patents/basics/apply/provisional-application']]
  },
  {
    slug: 'office-action-responses', name: 'Patent prosecution', group: 'Protect',
    short: 'Respond to examination with claim-focused reasoning, carefully supported amendments, and examiner engagement.',
    lead: 'Advance the application with a record that explains the invention clearly.',
    paragraphs: ['Examination brings the claims, disclosure, cited references, and examiner’s reasoning into direct conversation. A response should identify the actual point of disagreement and explain how the record supports the proposed position.', 'Work may include review of rejections and objections, amendment options, technical distinctions, examiner-interview preparation, and response drafting. Each proposed change is considered in the context of the application and the applicant’s objectives.'],
    includes: ['Office-action analysis and response planning', 'Prior-art mapping and technical distinctions', 'Claim amendments with disclosure support', 'Examiner interviews and interview summaries', 'Restriction and election responses', 'After-final options and request-for-continued-examination evaluation'],
    deliverables: ['Issue-by-issue response strategy', 'Marked and clean claim versions', 'Draft response and review questions'],
    fit: 'Applicants and patent counsel seeking focused assistance with pending U.S. applications.',
    scope: 'Timing and available procedural options must be confirmed from the actual application record; submitting an inquiry does not establish deadline monitoring.',
    related: ['patent-preparation', 'appeals-petitions', 'prior-art'],
    sources: [['MPEP § 714: amendments and applicant action', 'https://www.uspto.gov/web/offices/pac/mpep/s714.html']]
  },
  {
    slug: 'prior-art', name: 'Prior-art research & patentability', group: 'Analyze',
    short: 'Search the technical record and make the relationship between a disclosure and a proposed claim explicit.',
    lead: 'Useful research makes both the evidence and the limits of the search visible.',
    paragraphs: ['A search is most useful when it begins with a defined technical question. The research plan identifies concepts, alternative terminology, classifications, and the kinds of patent and non-patent literature most likely to matter.', 'Results are organized at the feature or limitation level, with source locators and a record of the search strategy. Analysis distinguishes what a reference actually discloses from what would require an inference or additional evidence.'],
    includes: ['Patent and non-patent literature searches', 'Feature and claim-limitation mapping', 'Search strategies, classifications, and terminology', 'Novelty and nonobviousness analysis for prosecution', 'Technical comparison of potentially relevant disclosures', 'Source provenance and reproducible search notes'],
    deliverables: ['Search report and reference library index', 'Source-supported comparison matrix', 'Gaps, assumptions, and follow-up questions'],
    fit: 'Teams evaluating a filing, responding to examination, or needing technical research to support counsel.',
    scope: 'No search can guarantee that every relevant reference has been found. Patentability analysis does not establish freedom to operate.',
    related: ['patent-preparation', 'claim-charting', 'technical-diligence'],
    sources: [['USPTO: search for patents', 'https://www.uspto.gov/patents/search']]
  },
  {
    slug: 'continuations-portfolio', name: 'Continuations & portfolio development', group: 'Protect',
    short: 'Connect pending claims, disclosed subject matter, and evolving technical priorities across an application family.',
    lead: 'Treat each filing as part of a considered patent record.',
    paragraphs: ['Portfolio development requires understanding what has been disclosed, what has been claimed, and how pending applications relate to one another. A structured family map makes those relationships easier to evaluate.', 'Work focuses on prosecution-related analysis: potential continuation or divisional claims, priority-support questions, prosecution history, and technical coverage relative to the applicant’s objectives. Business and transaction advice is coordinated with appropriate counsel.'],
    includes: ['Application-family and claim-set mapping', 'Continuation and divisional planning', 'Claim coverage relative to disclosed implementations', 'Priority and written-description support review', 'Prosecution history and consistency analysis', 'Technical portfolio triage'],
    deliverables: ['Family and priority map', 'Claim-coverage matrix', 'Prosecution options with recorded assumptions'],
    fit: 'Applicants maintaining a developing patent family and counsel seeking technical portfolio support.',
    scope: 'Continuation eligibility and timing depend on the specific family history and pending applications. No benefit claim is assumed without record review.',
    related: ['patent-preparation', 'office-action-responses', 'technical-diligence'],
    sources: [['MPEP Chapter 200: application types and benefit claims', 'https://www.uspto.gov/web/offices/pac/mpep/mpep-0200.html']]
  },
  {
    slug: 'pct-international', name: 'PCT & international coordination', group: 'Protect',
    short: 'Prepare and coordinate international patent work with a coherent technical disclosure and local counsel.',
    lead: 'Keep the invention consistent across a geographically complex filing strategy.',
    paragraphs: ['International patent work combines technical consistency with jurisdiction-specific requirements. U.S. and PCT preparation benefits from a clear disclosure record and a shared set of instructions for the professionals handling each jurisdiction.', 'Services can include PCT application preparation where authorized, U.S. national-stage work, analysis of international search findings, and coordination with qualified foreign associates. Local practitioners advise on and handle matters governed by their jurisdictions.'],
    includes: ['PCT drafting and filing preparation', 'U.S. national-stage application support', 'International search and written-opinion analysis', 'Technical instructions to foreign associates', 'Coordination of claim versions and responses', 'Priority-document and disclosure consistency review'],
    deliverables: ['Coordinated technical filing package', 'Jurisdiction and responsibility matrix', 'Consolidated claim and disclosure review notes'],
    fit: 'U.S. applicants pursuing an international filing pathway and foreign counsel seeking U.S. patent-agent support.',
    scope: 'A PCT application is not a worldwide patent. Foreign representation and jurisdiction-specific advice require appropriately qualified local practitioners.',
    related: ['patent-preparation', 'continuations-portfolio', 'office-action-responses'],
    sources: [['USPTO: Patent Cooperation Treaty', 'https://www.uspto.gov/patents/basics/international-protection/patent-cooperation-treaty']]
  },
  {
    slug: 'appeals-petitions', name: 'Ex parte appeals & patent-office petitions', group: 'Protect',
    short: 'Develop a focused patent-office record when continued examination calls for a different procedural path.',
    lead: 'Match the technical issue to the appropriate patent-office procedure.',
    paragraphs: ['When prosecution reaches an impasse, the first task is to identify the issue, the available record, and the procedural route that can address it. The analysis should distinguish an appealable rejection from a matter addressed through a petition.', 'Scoped assistance can include ex parte appeal analysis, brief preparation, technical support for argument, and patent-office petitions. Engagement depends on the issue, competence, capacity, deadlines, and the existing representation.'],
    includes: ['Ex parte appeal feasibility and issue review', 'Claim, evidence, and rejection mapping', 'Appeal and reply brief preparation', 'Technical argument development', 'Patent-office petition preparation within the agreed scope', 'Coordination with existing patent counsel'],
    deliverables: ['Procedural options and issue outline', 'Citation-supported draft submissions', 'Record and evidence index'],
    fit: 'Applicants and prosecution counsel evaluating a patent-office appeal or petition.',
    scope: 'This service concerns proceedings before the USPTO. Judicial appeals and court representation require an attorney authorized to handle them.',
    related: ['office-action-responses', 'prior-art', 'post-grant'],
    sources: [['MPEP Chapter 1200: appeal', 'https://www.uspto.gov/web/offices/pac/mpep/mpep-1200.html']]
  },
  {
    slug: 'design-patents', name: 'Design patent preparation & prosecution', group: 'Protect',
    short: 'Develop a drawing-led application directed to the ornamental appearance of an article of manufacture.',
    lead: 'Make the visual disclosure deliberate and internally consistent.',
    paragraphs: ['Design patent work starts with the appearance to be protected and the views needed to describe it. Drawing choices, consistency, and the treatment of claimed and unclaimed features deserve careful attention.', 'A scoped engagement can include design intake, coordination with a patent illustrator, preparation of the application, and responses during U.S. examination. Suitability and subject-matter fit are assessed before accepting the work.'],
    includes: ['Design disclosure and embodiment review', 'Patent-illustrator coordination', 'Drawing consistency and view review', 'Application preparation and filing support', 'Examiner-response preparation', 'Coordination with related utility filings'],
    deliverables: ['Coordinated application and drawing package', 'Drawing-review checklist', 'Examination response materials when engaged'],
    fit: 'Product teams, inventors, and counsel considering ornamental-design protection.',
    scope: 'Design and utility applications address different aspects of an invention. The appropriate protection strategy depends on the specific product and disclosure.',
    related: ['patent-preparation', 'office-action-responses', 'prior-art'],
    sources: [['MPEP Chapter 1500: design patents', 'https://www.uspto.gov/web/offices/pac/mpep/mpep-1500.html']]
  },
  {
    slug: 'post-grant', name: 'Reissue & ex parte reexamination', group: 'Protect',
    short: 'Evaluate selected patent-office mechanisms for addressing issues in an issued patent.',
    lead: 'Begin with the issued claims, the full record, and a precise objective.',
    paragraphs: ['An issued patent presents a different procedural setting from a pending original application. Reissue and ex parte reexamination serve distinct purposes, and neither should be selected without examining eligibility, scope, and consequences.', 'Scoped patent-office assistance can include technical and record analysis, preparation of supporting materials, and prosecution work where accepted. Related litigation and transaction questions are coordinated with appropriate counsel.'],
    includes: ['Issued-claim and prosecution-history review', 'Technical prior-art mapping', 'Reissue issue identification and application support', 'Ex parte reexamination request or response support', 'Evidence organization and citation verification', 'Coordination with litigation counsel where relevant'],
    deliverables: ['Technical record and issue matrix', 'Source-supported draft materials', 'Questions for coordinated procedural review'],
    fit: 'Patent owners and counsel evaluating a specifically identified patent-office issue.',
    scope: 'These are matter-specific services, subject to suitability and capacity review. No court representation or outcome is implied.',
    related: ['appeals-petitions', 'claim-charting', 'prior-art'],
    sources: [['MPEP Chapter 1400: reissue', 'https://www.uspto.gov/web/offices/pac/mpep/mpep-1400.html'], ['MPEP Chapter 2200: ex parte reexamination', 'https://www.uspto.gov/web/offices/pac/mpep/mpep-2200.html']]
  },
  {
    slug: 'claim-charting', name: 'Claim charts & technical litigation support', group: 'Analyze',
    short: 'Connect each claim limitation to inspectable technical evidence for review by litigation counsel.',
    lead: 'A conclusion is only as useful as the evidence that supports it.',
    paragraphs: ['Technical litigation work often turns on the connection between claim language and the operation of a real system. A useful analysis identifies the source, its version, the relevant passage or artifact, and the reasoning that connects it to a limitation.', 'Support can include infringement and invalidity chart preparation, source-code or technical-document review, expert-report support, and claim-construction research. Litigation strategy, legal opinions, filings, and court advocacy remain with the responsible attorneys.'],
    includes: ['Limitation-level infringement and invalidity charts', 'Software and technical-document review', 'Android APK/DEX and control-flow analysis', 'Semiconductor and wireless technical analysis', 'Expert-report and deposition preparation support', 'Evidence provenance and open-issue tracking'],
    deliverables: ['Traceable claim charts', 'Technical memoranda and annotated evidence', 'Unresolved questions and verification plan'],
    fit: 'Law firms, supervising experts, and in-house counsel handling technically demanding disputes.',
    scope: 'Provided as scientific and technical support to counsel. Layne Intellectual Property does not offer attorney representation in court.',
    related: ['prior-art', 'technical-diligence', 'research-systems'],
    sources: []
  },
  {
    slug: 'technical-diligence', name: 'Technical diligence & portfolio analysis', group: 'Analyze',
    short: 'Organize technical findings so counsel and business teams can evaluate the questions that matter.',
    lead: 'Make the technical basis for a decision inspectable.',
    paragraphs: ['A portfolio, product, or research program can contain more information than a decision-maker can readily use. Technical diligence distills that material into defined questions, supported findings, and clearly separated uncertainties.', 'Work can include claim-to-product mapping, patent-family research, technology landscapes, and technical inputs for counsel-led freedom-to-operate, licensing, or transaction reviews. Legal conclusions and agreements are handled by appropriate attorneys.'],
    includes: ['Technical patent portfolio triage', 'Claim-to-product and feature mapping', 'Patent landscape and family research', 'Technical inputs for counsel-led diligence', 'Evidence gaps and verification priorities', 'Scientific literature and technology assessments'],
    deliverables: ['Technical findings memorandum', 'Portfolio or technology comparison matrix', 'Evidence index and follow-up priorities'],
    fit: 'In-house legal teams, outside counsel, investors working with counsel, and research organizations.',
    scope: 'Technical support does not constitute a freedom-to-operate, infringement, or transaction opinion of counsel.',
    related: ['claim-charting', 'prior-art', 'continuations-portfolio'],
    sources: []
  },
  {
    slug: 'research-systems', name: 'Research & evidence workflows', group: 'Build',
    short: 'Build repeatable processes for source collection, claim versions, literature review, and technical verification.',
    lead: 'Give rigorous work a repeatable structure.',
    paragraphs: ['Repeatable research needs more than a folder of documents. It needs consistent source identifiers, explicit review states, version control, and a record of how an output was produced.', 'Workflow consulting connects these practices to real patent and scientific tasks. The aim is to make review and handoff easier through well-defined schemas, practical automation, and validation against representative work.'],
    includes: ['Source and evidence data models', 'Literature and prior-art review pipelines', 'Claim-version and document tracking', 'Research templates and quality checks', 'Human-reviewed AI workflow design', 'Reproducibility and technical documentation'],
    deliverables: ['Documented workflow and data schema', 'Review templates or scoped prototype', 'Verification checks and handoff notes'],
    fit: 'Patent teams, scientific groups, and organizations seeking more consistent research operations.',
    scope: 'Software and automation support professional review. They do not provide autonomous patentability decisions or replace practitioner judgment.',
    related: ['claim-charting', 'prior-art', 'technical-diligence'],
    sources: []
  }
];

export const technologies = [
  {slug:'semiconductors-hardware',name:'Semiconductors & hardware',label:'Architecture / devices / circuitry',summary:'From microarchitecture and power management to the system behavior a claim is intended to describe.',body:'The analysis connects components, signals, operating states, and architectural constraints. Technical experience includes semiconductor patent analysis involving microprocessors, power management circuitry, and data-processing technologies.',topics:['Microprocessor architecture','Power management and circuitry','Memory and data paths','System-on-chip integration','Electronic and embedded systems'],questions:['Which component performs each claimed function?','How do timing, state, and control relationships affect the technical reading?','Which documents or measurements can verify the implementation?'],services:['claim-charting','prior-art','patent-preparation']},
  {slug:'software-ai',name:'Software, AI & data systems',label:'Code / models / infrastructure',summary:'Technical detail across source code, deployed systems, model workflows, and information processing.',body:'Software analysis benefits from a view of both the described architecture and the code or artifacts that implement it. The work can connect data flow, control flow, interfaces, and dependencies to the patent question under review.',topics:['Software architectures and APIs','AI and machine-learning workflows','Android applications and reverse engineering','Distributed and cloud systems','Data processing and analytics'],questions:['What transforms the data, and where does that transformation occur?','Which implementation details distinguish the disclosed approach?','Can the asserted behavior be reproduced from the available artifacts?'],services:['patent-preparation','claim-charting','research-systems']},
  {slug:'wireless-connectivity',name:'Wireless & connectivity',label:'Protocols / networks / devices',summary:'A structured view of communication protocols, device behavior, and evidence from real systems.',body:'Wireless technologies require careful treatment of protocol layers, device configuration, and implementation-specific behavior. The technical record may include specifications, packet captures, logs, source code, and controlled experimental observations.',topics:['Cellular and Wi-Fi systems','OFDMA and protocol analysis','Device-level network behavior','Radio-concurrency investigation planning','Network logs and packet evidence'],questions:['Which protocol layer contains the relevant behavior?','What does a source establish about the particular device or version?','What controls are needed to test competing explanations?'],services:['claim-charting','prior-art','technical-diligence']},
  {slug:'biotechnology',name:'Biotechnology & molecular biology',label:'Biological systems / assays / discovery',summary:'Patent work informed by doctoral training in cell and molecular biology and experimental neuroscience.',body:'A scientific disclosure must connect its biological mechanism with the methods, materials, and observations that support it. Research training helps make experimental assumptions, alternative implementations, and the limits of the available evidence explicit.',topics:['Molecular and cellular biology','Genetic and viral tools','Assay development and analytical methods','Neuroscience and electrophysiology','Bioinformatics and computational biology'],questions:['What is the demonstrated result and what remains a hypothesis?','Which experimental conditions materially affect reproducibility?','How do the disclosed examples relate to the proposed claims?'],services:['patent-preparation','office-action-responses','prior-art']},
  {slug:'pharmaceuticals-chemistry',name:'Pharmaceuticals & analytical chemistry',label:'Compositions / methods / measurement',summary:'Close attention to structure, function, experimental support, and the boundaries of a scientific disclosure.',body:'Pharmaceutical and analytical technologies call for deliberate organization of the disclosed compounds, compositions, methods, and data. Preparation and analysis focus on the relationship between the technical disclosure and the intended patent position.',topics:['Pharmaceutical compositions and methods','Formulation and delivery concepts','Analytical chemistry platforms','Assays and measurement workflows','Structure–function and experimental support'],questions:['Which features account for the reported technical effect?','What variations are disclosed and supported by the record?','How do the application and references describe comparable conditions?'],services:['patent-preparation','pct-international','prior-art']},
  {slug:'medical-research-technologies',name:'Medical & research technologies',label:'Instruments / diagnostics / interfaces',summary:'Where engineered systems meet biological measurement, diagnostics, and scientific investigation.',body:'Research and medical technologies frequently combine hardware, software, and life sciences. A useful patent analysis identifies how those elements interact and where the technical contribution resides.',topics:['Research instrumentation','Diagnostics and optical detection','Microfluidic and cell-analysis platforms','Image processing and robotic vision','Digital health and biomedical data'],questions:['Which parts of the system work together to produce the result?','What is measured, computed, or controlled?','Which source evidence distinguishes a capability from an implementation?'],services:['patent-preparation','claim-charting','technical-diligence']}
];

export const professionals = [{
  slug:'robert-m-layne',name:'Robert M. Layne, Ph.D.', initials:'RML',lastName:'Layne',role:'Patent Agent & Scientific Advisor',
  disciplines:['Hardware','Software & AI','Life sciences','Evidence systems'],
  tags:'hardware semiconductors software ai life sciences pharmaceuticals chemistry biology evidence systems wireless research patent',
  bio:['Robert M. Layne, Ph.D., is a U.S. patent agent and scientific advisor whose work connects patent prosecution, technical analysis, and reproducible research. He brings a Ph.D. in Cell and Molecular Biology and experience across life sciences, semiconductor technologies, software, and wireless systems.',
  'His professional experience includes patent drafting and prosecution, infringement and invalidity claim charts, Android reverse engineering, and preparation of technical materials for supervising experts and litigation counsel. His work emphasizes source traceability, clear methods, and precise communication between technical and legal teams.',
  'Before entering patent practice, Dr. Layne conducted neuroscience research at the University of Maryland and Michigan Medicine. His research background includes electrophysiology, neuronal circuit mapping, experimental design, and computational analysis.'],
  education:[['Ph.D., Cell and Molecular Biology','University of Toledo · 2015'],['B.S., Neuroscience and Philosophy; minor in Chemistry','University of Pittsburgh · 2008']],
  experience:[['Layne Intellectual Property','Patent Agent & Scientific Advisor','December 2024–present'],['Quandary Peak Research','Senior Consultant','September 2023–December 2024'],['Kramer Levin Naftalis & Frankel LLP','Scientific Advisor','April 2022–March 2023'],['Irell & Manella LLP','Technology Specialist','January 2020–July 2021'],['University of Maryland','Postdoctoral Associate','July 2016–October 2018'],['Michigan Medicine','Postdoctoral Associate','September 2015–July 2016']],
  source:'2026-02-26_CV.docx', registration:'82,283',
  email:'robert@layneip.com', phone:'+1 (571) 274-0684', telephone:'+15712740684', contactFile:'/robert-m-layne.vcf',
  profileTitle:'A scientific approach to technically demanding work.', profileLede:'Patent prosecution. Technical evidence. Scientific perspective.',
  publicationIds:['ai-inference','retina-brain-pathways','sensory-integration']
}];

export const publications = [
  {slug:'ai-inference',title:'AI Inference: Legal Challenges in Deploying Machine Learning Models',category:'AI & technology',type:'Article',publisher:'Quandary Peak Research',date:'2024-07-08',author:'Robert Layne',summary:'An article examining IP, privacy, explainability, and accountability questions associated with deploying machine-learning models. Published in 2024; read in its original context.',url:'https://quandarypeak.com/2024/07/ai-inference-challenges-in-deploying-ml-models/'},
  {slug:'retina-brain-pathways',title:'Light Affects Mood and Learning through Distinct Retina-Brain Pathways',category:'Scientific research',type:'Research paper',publisher:'Cell',date:'2018-09-20',author:'Fernandez et al.; coauthor Robert M. Layne',summary:'Collaborative neuroscience research on pathways linking retinal input to mood and learning.',url:'https://pubmed.ncbi.nlm.nih.gov/30173913/'},
  {slug:'sensory-integration',title:'Multiple Sensory Inputs Are Extensively Integrated to Modulate Nociception in C. elegans',category:'Scientific research',type:'Research paper',publisher:'The Journal of Neuroscience',date:'2015-07-15',author:'Summers, Layne et al.; co-first author Robert M. Layne',summary:'Research examining sensory integration and the modulation of nociceptive behavior.',url:'https://doi.org/10.1523/JNEUROSCI.0225-15.2015'}
];

export const faqs = [
 ['What can a U.S. patent agent do?', 'A registered patent agent can represent others in patent matters before the USPTO, including patent preparation and prosecution within the authorized scope of practice. A patent agent is not, by that registration alone, an attorney. Court litigation, general legal advice, and transactional agreements require appropriately qualified counsel.'],
 ['Do you work with outside patent and litigation counsel?', 'Yes. An engagement can focus on a defined prosecution task, technical analysis, claim chart, source-code review, or expert-support assignment. Responsibilities, supervision where applicable, deliverables, and deadlines are established in the engagement.'],
 ['Can I send an invention disclosure with my first inquiry?', 'Start with a high-level, non-confidential description of the technology and the help you need. Confidential documents and detailed disclosures should wait until conflicts, scope, engagement, and the appropriate method of exchange have been addressed.'],
 ['Can you handle an urgent deadline?', 'Identify the date and the type of deadline in your inquiry. Availability and responsibility for any deadline must be expressly confirmed; an email or website inquiry alone does not establish an engagement or deadline monitoring.'],
 ['Do you offer fixed-fee or phased work?', 'Fees and scope are set for each engagement. A phased or fixed-fee structure can be considered when the inputs, deliverables, assumptions, and review process can be defined clearly. No pricing commitment is made by this website.'],
 ['Can you support work outside the United States?', 'U.S. and authorized PCT work can be coordinated with qualified foreign associates. Foreign patent-office representation and jurisdiction-specific advice are provided by practitioners authorized in the relevant jurisdiction.'],
 ['Does a patentability search establish freedom to operate?', 'No. Patentability and freedom to operate ask different questions. Patentability addresses whether an invention may qualify for patent protection; freedom-to-operate work examines potential rights affecting a proposed activity and may require legal opinions from qualified counsel.'],
 ['How are AI and automation used?', 'Potential uses are evaluated for the task, data sensitivity, verification requirements, and engagement terms. Sources and outputs must remain reviewable. The website does not provide an automated legal opinion, and professional judgment remains with the responsible practitioner.']
];
