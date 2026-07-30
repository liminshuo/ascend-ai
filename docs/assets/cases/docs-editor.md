> ## Documentation Index
> Fetch the complete documentation index at: https://www.mintlify.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Editor overview

> Create, edit, and publish content in your browser with real-time team collaboration, automatic saving, live previews, and continuous Git sync.

<Card title="New to the editor? Start with the tutorial." icon="graduation-cap" horizontal href="/docs/editor/tutorial">
  A step-by-step walkthrough: create a branch, make a change, share a preview, and publish.
</Card>

## Open the editor

Open the editor from the [Editor](https://app.mintlify.com/editor) tab in your Mintlify dashboard. Any member of your organization can open the editor, but what you can do inside depends on your [role](/docs/dashboard/roles). Admins and editors can edit and publish, and viewers can browse content and leave [comments](/docs/editor/comments) or [suggestions](/docs/editor/suggestions).

## How the editor works

**Changes save automatically.** As you type, the editor saves your work. Your changes persist across tabs, devices, and network interruptions. Changes only go live when you publish them.

**Git stays in sync.** When someone else pushes changes to your repository from outside the editor, those changes appear in the editor automatically. You don't need to pull or refresh. The editor merges non-conflicting changes and highlights anything that needs your attention.

<Tip>
  If the editor ever appears out of sync with your repository, use [Reset editor](/docs/editor/settings#reset-editor) to force a resync from Git. For example, the file tree is empty or shows `Unable to find docs.json` even though the file is present on your deployment branch.
</Tip>

**Publishing writes to Git.** When you publish, the editor commits your changes to your repository. On a deployment branch, this updates your live site immediately. On a feature branch, it creates a pull request.

**Your team edits together.** Multiple people can edit the same page simultaneously. Live cursors show who is editing and where.

## The editor layout

<Frame>
  <img src="https://mintcdn.com/mintlify/yLHAwTnwTq05X1uS/images/editor/editor-layout-light.png?fit=max&auto=format&n=yLHAwTnwTq05X1uS&q=85&s=c77d11b14d15c8853724fb67afa2af13" alt="Screenshot of the editor showing the branch selector, ask agent button, publish button, navigation sidebar, and top bar." className="block dark:hidden" width="2537" height="420" data-path="images/editor/editor-layout-light.png" />

  <img src="https://mintcdn.com/mintlify/yLHAwTnwTq05X1uS/images/editor/editor-layout-dark.png?fit=max&auto=format&n=yLHAwTnwTq05X1uS&q=85&s=a8258f4b6fea8ac3310350cde8390208" alt="Screenshot of the editor showing the branch selector, ask agent button, publish button, navigation sidebar, and top bar." className="hidden dark:block" width="2537" height="420" data-path="images/editor/editor-layout-dark.png" />
</Frame>

* **Top bar**: Use the top bar to control what branch you work on, access the agent, preview, and publish changes.
* **Navigation sidebar**: Select a page to edit, create new pages, and manage the site structure.

## Explore the editor

<Card title="Branching and publishing" icon="git-branch" horizontal href="/docs/editor/branching-and-publishing">
  How branches and protection rules determine what happens when you publish, and how to manage the pull request review process.
</Card>

<Card title="Comments" icon="message-square" horizontal href="/docs/editor/comments">
  Leave feedback, ask questions, and discuss changes with your team.
</Card>

<Card title="Suggestions" icon="pen-line" horizontal href="/docs/editor/suggestions">
  Propose changes that teammates can review, accept, or reject.
</Card>

<Card title="Ask agent" icon="sparkles" horizontal href="/docs/editor/agent">
  Edit pages, search your content, modify settings, and configure your site from a chat interface.
</Card>

<Card title="Create and edit pages" icon="notebook-pen" horizontal href="/docs/editor/pages">
  Add new and update existing pages.
</Card>

<Card title="Organize navigation" icon="list-tree" horizontal href="/docs/editor/navigation">
  Reorder pages and manage site structure.
</Card>

<Card title="Live preview" icon="play" horizontal href="/docs/editor/live-preview">
  Preview your site in real time as you edit without waiting for a build.
</Card>

<Card title="Configurations" icon="sliders-horizontal" horizontal href="/docs/editor/configurations">
  Configure your site's branding, colors, and features.
</Card>

<Card title="Settings" icon="settings" horizontal href="/docs/editor/settings">
  Configure AI instructions and publishing defaults for your deployment.
</Card>

<Card title="Git essentials" icon="git-merge" horizontal href="/docs/editor/git-essentials">
  Understand the Git concepts behind the editor: branches, commits, pull requests, and merges.
</Card>

<Card title="Keyboard shortcuts" icon="keyboard" horizontal href="/docs/editor/keyboard-shortcuts">
  Save time with keyboard shortcuts.
</Card>


## Related topics

- [Editor overview](/docs/editor/index.md)
- [Automations overview](/docs/automations/index.md)
- [API playground overview](/docs/api-playground/overview.md)
