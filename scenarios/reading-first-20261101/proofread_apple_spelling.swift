import AppKit
import Foundation
import NaturalLanguage

// Local macOS spelling witness. This is advisory, not authorship or
// a source edit; foreign names/poetry/typographic diction may be intentional.
guard CommandLine.arguments.count == 3 else {
    fputs("usage: proofread_apple_spelling.swift audit-input.json audit-output.json\n", stderr)
    exit(2)
}
let input = URL(fileURLWithPath: CommandLine.arguments[1])
let output = URL(fileURLWithPath: CommandLine.arguments[2])
let data = try Data(contentsOf: input)
guard let root = try JSONSerialization.jsonObject(with: data) as? [String:Any],
      let works = root["works"] as? [[String:Any]] else {
    fputs("invalid source-owned Reader data\n", stderr);exit(2)
}
let checker = NSSpellChecker.shared
var results: [[String:Any]] = []
for work in works {
    guard let id=work["id"] as? String, let title=work["title"] as? String,
          let plain=work["text"] as? String else {continue}
    guard id.hasPrefix("essay--") || id.hasPrefix("solstice-reading-01--") || id=="teatro" else {continue}
    let lang=NLLanguageRecognizer.dominantLanguage(for: String(plain.prefix(10000)))
    let language = lang == .german ? "de" : "en"
    let ns=plain as NSString
    var offset = 0, candidates: [String] = []
    var previous = -1
    let end=ns.length
    while offset < end && candidates.count < 220 {
        let result=checker.checkSpelling(of: plain, startingAt: offset, language: language,
            wrap:false, inSpellDocumentWithTag:0, wordCount:nil)
        if result.location == NSNotFound || result.length <= 0 || result.location <= previous {break}
        let token=ns.substring(with: result)
        // Filtering only punctuation/ASCII artifact; leave foreign terms for review.
        if token.count >= 3 && token.rangeOfCharacter(from: CharacterSet.letters) != nil {
            candidates.append(token)
        }
        previous=result.location
        offset=result.location + result.length
    }
    let distinct=Array(Set(candidates)).sorted()
    results.append(["id":id,"title":title,"language":language,
       "spellingCandidates":Array(distinct.prefix(80)),
       "distinctCount":distinct.count,
       "status":"manual editorial verification required; literary terms and names may be intentional"])
    print("APPLE_SPELL_AUDIT",id,language,"distinctCandidates",distinct.count)
}
let report:[String:Any]=["schema":"fountain.press.apple-native-local-spelling-audit.v1",
   "privacy":"local Mac spelling and language recognition; no external request",
   "authority":"Advisory only; exact writer manuscript unchanged",
   "works":results]
let buf=try JSONSerialization.data(withJSONObject:report,options:[.prettyPrinted,.sortedKeys])
try buf.write(to: output)
print("APPLE_SPELL_AUDIT_COMPLETE",results.count,output.path)
