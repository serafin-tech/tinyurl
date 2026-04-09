<script lang="ts">
  import './style.css'
  import { createLink, updateLink, deleteLink, getLink, type CreateLinkPayload, type CreateLinkResponse, type LinkOut } from './lib/api'

  let createForm = $state<CreateLinkPayload>({ target_url: '', link_id: '', redirect_code: 301 })
  let createResult = $state<CreateLinkResponse | null>(null)
  let createError = $state<string | null>(null)

  let updLinkId = $state('')
  let updToken = $state('')
  let updTarget = $state('')
  let updCode = $state<301 | 302 | 307 | 308 | ''>('')
  let updNewAlias = $state('')
  let updError = $state<string | null>(null)
  let updResult = $state<unknown>(null)

  let delLinkId = $state('')
  let delToken = $state('')
  let delError = $state<string | null>(null)
  let delResult = $state<unknown>(null)

  const redirectTester = $state<{
    linkId: string
    status: string
    location: string
    active: boolean | null
  }>({
    linkId: '',
    status: '',
    location: '',
    active: null
  })

  async function onCreate() {
    createError = null
    createResult = null
    try {
      const payload: CreateLinkPayload = {
        target_url: createForm.target_url,
        link_id: createForm.link_id || undefined,
        redirect_code: createForm.redirect_code
      }
      createResult = await createLink(payload)
    } catch (e: unknown) {
      createError = e instanceof Error ? e.message : String(e)
    }
  }

  async function onUpdate() {
    updError = null
    updResult = null
    try {
      const data: Record<string, unknown> = {}
      if (updTarget) data.target_url = updTarget
      if (updCode) data.redirect_code = updCode
      if (updNewAlias) data.new_link_id = updNewAlias
      updResult = await updateLink(updLinkId, updToken, data)
    } catch (e: unknown) {
      updError = e instanceof Error ? e.message : String(e)
    }
  }

  async function onDelete() {
    delError = null
    delResult = null
    try {
      delResult = await deleteLink(delLinkId, delToken)
    } catch (e: unknown) {
      delError = e instanceof Error ? e.message : String(e)
    }
  }

  async function testRedirect() {
    redirectTester.status = ''
    redirectTester.location = ''
    redirectTester.active = null
    try {
      const link: LinkOut = await getLink(redirectTester.linkId)
      redirectTester.status = String(link.redirect_code)
      redirectTester.location = link.target_url
      redirectTester.active = link.active
    } catch (e: unknown) {
      redirectTester.status = 'error'
      redirectTester.location = e instanceof Error ? e.message : String(e)
    }
  }
</script>

<div class="container">
  <h1>TinyURL UI</h1>

  <div class="card">
    <h2>Create short link</h2>
    <label>Target URL</label>
    <input bind:value={createForm.target_url} placeholder="https://example.com" />
    <div class="grid">
      <div>
        <label>Custom alias (optional)</label>
        <input bind:value={createForm.link_id} placeholder="my-alias" />
      </div>
      <div>
        <label>Redirect code</label>
        <select bind:value={createForm.redirect_code}>
          <option value={301}>301</option>
          <option value={302}>302</option>
          <option value={307}>307</option>
          <option value={308}>308</option>
        </select>
      </div>
    </div>
    <button onclick={onCreate}>Create</button>
    {#if createError}
      <p class="small">Error: {createError}</p>
    {/if}
    {#if createResult}
      <pre>{JSON.stringify(createResult, null, 2)}</pre>
    {/if}
  </div>

  <div class="card">
    <h2>Update link</h2>
    <label>Link ID</label>
    <input bind:value={updLinkId} placeholder="existing-id" />
    <label>Edit token</label>
    <input bind:value={updToken} placeholder="paste edit token" />
    <div class="grid">
      <div>
        <label>New target URL</label>
        <input bind:value={updTarget} placeholder="https://example.com/new" />
      </div>
      <div>
        <label>New redirect code</label>
        <select bind:value={updCode}>
          <option value="">(no change)</option>
          <option value={301}>301</option>
          <option value={302}>302</option>
          <option value={307}>307</option>
          <option value={308}>308</option>
        </select>
      </div>
    </div>
    <label>Change alias to</label>
    <input bind:value={updNewAlias} placeholder="new-alias" />
    <button onclick={onUpdate}>Update</button>
    {#if updError}
      <p class="small">Error: {updError}</p>
    {/if}
    {#if updResult}
      <pre>{JSON.stringify(updResult, null, 2)}</pre>
    {/if}
  </div>

  <div class="card">
    <h2>Delete link</h2>
    <label>Link ID</label>
    <input bind:value={delLinkId} placeholder="existing-id" />
    <label>Edit token</label>
    <input bind:value={delToken} placeholder="paste edit token" />
    <button onclick={onDelete}>Delete</button>
    {#if delError}
      <p class="small">Error: {delError}</p>
    {/if}
    {#if delResult}
      <pre>{JSON.stringify(delResult, null, 2)}</pre>
    {/if}
  </div>

  <div class="card">
    <h2>Redirect tester</h2>
    <label>Link ID</label>
    <input bind:value={redirectTester.linkId} placeholder="id-to-test" />
    <button onclick={testRedirect}>Test</button>
    <p class="small">Redirect code: {redirectTester.status} | Target: {redirectTester.location} | Active: {redirectTester.active ?? '—'}</p>
  </div>
</div>
