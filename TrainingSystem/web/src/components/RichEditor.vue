<template>
    <div class="rich-editor-container">
      <div 
        ref="editorRef"
        class="editor-content"
        contenteditable="true"
        @input="onInput"
        @paste="onPaste"
        :placeholder="placeholder"
      ></div>
      
      <div v-if="uploading" class="upload-loading">
        <span>🚀 正在上传图片...</span>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, watch } from 'vue'
  import { ElMessage } from 'element-plus'
  import http from '../http'
  
  const props = defineProps({
    modelValue: String,
    placeholder: String,
    reportId: [Number, String]
  })
  
  const emit = defineEmits(['update:modelValue'])
  const editorRef = ref(null)
  const uploading = ref(false)
  
  onMounted(() => {
    if (editorRef.value) {
      editorRef.value.innerHTML = props.modelValue || ''
    }
  })
  
  // 双向绑定监听
  watch(() => props.modelValue, (newVal) => {
    if (editorRef.value && editorRef.value.innerHTML !== newVal) {
      if (!editorRef.value.innerHTML || editorRef.value.innerHTML === '<br>') {
        editorRef.value.innerHTML = newVal || ''
      }
    }
  })
  
  const onInput = () => {
    emit('update:modelValue', editorRef.value.innerHTML)
  }
  
  // ★★★ 核心：粘贴事件处理 ★★★
  const onPaste = async (e) => {
    const items = (e.clipboardData || e.originalEvent.clipboardData).items
    let blob = null
    
    // 1. 寻找剪贴板里的图片
    for (const item of items) {
      if (item.type.indexOf('image') !== -1) {
        blob = item.getAsFile()
        break
      }
    }
  
    // 2. 如果是图片，拦截默认行为，执行上传
    if (blob) {
      e.preventDefault() 
      
      if (!props.reportId) {
        return ElMessage.warning('请先等待草稿自动保存后再粘贴图片')
      }
  
      uploading.value = true
      const fd = new FormData()
      fd.append('file', blob, 'paste_image.png')
  
      try {
        // 调用后端接口
        const res = await http.post(`reports/${props.reportId}/upload_attachment/`, fd)
        const imgUrl = res.data.url // 获取图片地址
        
        // 3. 在光标位置插入图片
        insertImage(imgUrl)
        
        onInput() // 触发保存
        ElMessage.success('截图已插入')
      } catch (err) {
        console.error(err)
        ElMessage.error('图片上传失败，请重试')
      } finally {
        uploading.value = false
      }
    }
  }
  
  // 插入图片并换行
  const insertImage = (url) => {
    const img = document.createElement('img')
    img.src = url
    img.className = 'editor-image' // 应用下方定义的样式
    
    const sel = window.getSelection()
    if (sel.rangeCount) {
      const range = sel.getRangeAt(0)
      range.deleteContents()
      range.insertNode(img)
      
      // 插入后光标移动到图片后面并换行，方便继续打字
      range.collapse(false)
      const br = document.createElement('br')
      range.insertNode(br)
      range.collapse(false)
    } else {
      editorRef.value.appendChild(img)
    }
  }
  </script>
  
  <style>
  /* ★★★ 全局样式：控制编辑器内的图片显示 ★★★ */
  /* 这里的样式不加 scoped，是为了能控制动态插入的 img 标签 */
  .editor-content .editor-image {
    max-width: 100%;      /* 宽度撑满容器 */
    height: auto;         /* 高度自适应 */
    display: block;       /* 独占一行 */
    margin: 15px 0;       /* 上下留白 */
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1); /* 给截图加一点阴影，更好看 */
    border: 1px solid #eee;
  }
  </style>
  
  <style scoped>
  .rich-editor-container {
    position: relative;
    width: 100%;
  }
  
  .editor-content {
    min-height: 150px;
    border: 1px solid #dcdfe6;
    border-radius: 0; /* 保持和其他输入框一致的直角风格 */
    padding: 15px;
    background: #fff;
    font-size: 15px;
    line-height: 1.6;
    color: #333;
    outline: none;
    white-space: pre-wrap;
    overflow-y: hidden; /* 高度随内容自动撑开 */
  }
  
  .editor-content:focus {
    border-color: #409EFF;
    background-color: #fcfcfc;
  }
  
  /* 模拟 placeholder */
  .editor-content:empty:before {
    content: attr(placeholder);
    color: #999;
    font-size: 14px;
  }
  
  .upload-loading {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(255,255,255,0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #409EFF;
    font-weight: bold;
    z-index: 5;
  }
  </style>