// Drafts are included only in private-review builds. Set status to published after editorial review.
export const articles = [
  {
    slug:'working-with-a-patent-agent', title:'Working with a patent agent: the scope of the engagement',
    category:'Patent practice', status:'draft', date:'2026-09-21', author:'Layne Intellectual Property',
    summary:'How patent-office representation and technical support fit together—and where attorney involvement belongs.',
    sections:[
      ['Begin with the kind of work', ['A useful first question is not simply whether a matter involves a patent. It is what work needs to be performed, before which institution, and by whom. Preparing a U.S. application, responding to an examiner, analyzing source code for litigation counsel, and negotiating a license are distinct assignments.', 'A registered U.S. patent agent can represent others in authorized patent matters before the USPTO. The USPTO’s rules and guidance distinguish that role from attorney practice. The registration does not, by itself, authorize representation in a court or the full range of legal services offered by a law firm.']],
      ['Define the record and the deliverable', ['For a prosecution engagement, the relevant record may include the application, claims, cited references, office actions, and filing history. An agreed deliverable might be an application draft, a response, or an analysis of available prosecution options.', 'For counsel-directed technical work, the deliverable may instead be a claim chart, evidence matrix, code analysis, or expert-support memorandum. The engagement should identify the responsible counsel and the boundary between technical findings and legal conclusions.']],
      ['Confirm responsibilities before work begins', ['A written scope should identify the client, conflicts review, responsible professionals, fees, expected deliverables, and responsibility for deadlines. Availability should never be inferred from a website inquiry or an unanswered email.', 'The first communication can remain brief and non-confidential: the parties involved, the general technology, the assistance requested, and any known dates. Detailed invention materials can be exchanged through an agreed channel after the engagement requirements have been addressed.']]
    ],
    sources:[['USPTO MPEP § 401: representation by a patent practitioner','https://www.uspto.gov/web/offices/pac/mpep/s401.html'],['USPTO MPEP § 402: representation and recognition','https://www.uspto.gov/web/offices/pac/mpep/s402.html']]
  },
  {
    slug:'prepare-for-an-invention-discussion', title:'Prepare for a productive invention discussion',
    category:'Patent practice', status:'draft', date:'2026-09-21', author:'Layne Intellectual Property',
    summary:'A practical way to organize the problem, implementation, alternatives, evidence, and known dates.',
    sections:[
      ['Explain the technical problem', ['Begin with the condition the invention addresses. Describe how an existing approach operates, where it falls short, and which constraints shape the proposed solution. A precise problem statement helps distinguish the invention from a list of desirable results.', 'Describe an implementation in enough detail that another technical reader can follow it. Identify components, operations, inputs, outputs, and the relationships that make the system work. In a scientific context, record materials, conditions, measurements, and controls.']],
      ['Separate demonstrations from possibilities', ['Mark what has actually been built, tested, or observed. Keep proposed variations and future experiments visible as such. This distinction makes the disclosure easier to evaluate and avoids silently treating a hypothesis as an experimental result.', 'Alternative implementations deserve attention. Consider which details are essential to the result and which may vary. Record the reasoning behind those distinctions so the drafting discussion can examine them rather than assume them.']],
      ['Bring the relevant history', ['Prepare a chronology of known publications, presentations, offers for sale, demonstrations, disclosures, and earlier filings. Include the available documents and identify uncertain dates. Their legal significance must be assessed for the particular circumstances and jurisdictions.', 'For an initial inquiry, send only a non-confidential outline. Once an engagement and an appropriate exchange method are established, the detailed disclosure, diagrams, laboratory materials, and development records can support a focused review.']]
    ],
    sources:[['USPTO: applying for a patent','https://www.uspto.gov/patents/basics/apply'],['USPTO: provisional applications','https://www.uspto.gov/patents/basics/apply/provisional-application']]
  },
  {
    slug:'traceable-claim-charts', title:'What makes a claim chart reviewable?',
    category:'Evidence & systems', status:'draft', date:'2026-09-21', author:'Layne Intellectual Property',
    summary:'Keep the claim version, source locator, technical reasoning, and unresolved questions connected.',
    sections:[
      ['Fix the inputs before mapping the evidence', ['A chart should identify the patent, the claim number, and the exact claim version under analysis. It should also identify the source version. A citation to a changing webpage or an unspecified software build can leave the reviewer unable to reproduce the analysis.', 'Divide the claim into usable analytical units without losing the relationships expressed by the complete claim. The segmentation is an organizational aid; it is not itself a claim construction.']],
      ['Keep evidence and reasoning separate', ['For each limitation, preserve the relevant passage, figure, code location, or observed artifact. Add a locator precise enough for another reviewer to reach it. Then explain why that evidence is relevant to the limitation.', 'Label direct observations, assumptions, and inferences. If a source supports only part of a limitation, record the remaining gap. An unsupported cell should remain an open question instead of becoming a confident conclusion by repetition.']],
      ['Make the handoff reproducible', ['A review package can include the chart, an evidence manifest, a source index, and a short list of questions requiring follow-up. For software or measurement evidence, record the environment and relevant procedures as well.', 'The evidence-manifest utility on this site illustrates the source-index portion of that workflow. It organizes metadata and can compute a file checksum locally. A checksum can help identify whether bytes have changed; it does not establish authenticity, completeness, privilege, or a legal conclusion.']]
    ],
    sources:[], methodology:true
  }
];
