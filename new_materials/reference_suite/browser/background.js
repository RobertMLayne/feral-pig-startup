chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({ id: "reference-suite-intake", title: "Capture in Reference Suite", contexts: ["selection"] });
});

chrome.contextMenus.onClicked.addListener((info) => {
  if (info.menuItemId === "reference-suite-intake" && info.selectionText) {
    chrome.storage.local.set({ selectedReference: info.selectionText.trim() });
    chrome.action.openPopup().catch(() => {});
  }
});
