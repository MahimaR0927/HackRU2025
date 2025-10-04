<script>
  let file;
  let tag = "";
  let previewSrc = "";

  function showClothing() {
    if (!file) {
      alert("Please select an image");
      return;
    }
    previewSrc = URL.createObjectURL(file);
  }
</script>

<h1>Product Name</h1>

<p>
  This app lets you update photos of all your clothing and
  the AI system will choose your outfit for the day.
</p>

<label for="clothing">Choose an image</label>
<input type="file" id="clothing" accept="image/*" bind:files={file}>

<label for="fit">Enter a tag for clothing</label>
<input type="text" id="fit" placeholder="Pick a style" bind:value={tag}>

<button on:click={showClothing}>Submit</button>

<div>
  {#if previewSrc}
    <img src={previewSrc} width="300" height="300"><br>
    <span>Tag: {tag}</span>
  {/if}
</div>

<style>
  h1 { color: purple; }
  p { font-size: 16px; }
  div { margin-top: 10px; }
</style>
