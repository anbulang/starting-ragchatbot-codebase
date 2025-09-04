# /api/query 接口流程图

```mermaid
graph TD
    A[客户端发送POST请求到/api/query] --> B{检查session_id是否存在?}
    
    B -->|否| C[创建新的会话ID]
    B -->|是| D[使用现有会话ID]
    
    C --> E[调用RAG系统处理查询]
    D --> E
    
    E --> F[构建AI提示词]
    F --> G[获取会话历史记录]
    G --> H[调用AI生成器]
    
    H --> I{AI是否需要使用搜索工具?}
    
    I -->|是| J[执行搜索工具]
    I -->|否| K[直接返回AI响应]
    
    J --> L[向量存储搜索]
    L --> M[课程名称解析]
    M --> N[构建过滤条件]
    N --> O[ChromaDB语义搜索]
    O --> P[格式化搜索结果]
    P --> Q[AI基于搜索结果生成最终响应]
    
    Q --> R[更新会话历史]
    K --> R
    
    R --> S[返回QueryResponse]
    S --> T[包含答案、来源和会话ID]
    
    subgraph "RAG系统组件"
        E1[文档处理器]
        E2[向量存储]
        E3[AI生成器]
        E4[会话管理器]
        E5[搜索工具管理器]
    end
    
    subgraph "向量存储详细流程"
        L1[接收搜索查询]
        L2[解析课程名称]
        L3[构建ChromaDB过滤器]
        L4[执行语义搜索]
        L5[返回搜索结果]
    end
    
    subgraph "AI生成器详细流程"
        H1[构建系统提示词]
        H2[添加会话历史]
        H3[调用Claude API]
        H4[处理工具调用]
        H5[生成最终响应]
    end
```

## 详细流程说明

### 1. 请求接收阶段
- 客户端发送POST请求到 `/api/query`
- 请求包含 `query`（用户问题）和可选的 `session_id`

### 2. 会话管理
- 如果没有提供 `session_id`，系统会创建一个新的会话
- 如果提供了 `session_id`，系统会使用现有会话

### 3. RAG系统处理
- 调用 `rag_system.query()` 方法
- 构建AI提示词
- 获取会话历史记录（如果存在）

### 4. AI生成器处理
- 调用 `ai_generator.generate_response()`
- 传递查询、会话历史和可用工具
- AI决定是否需要使用搜索工具

### 5. 搜索工具执行（如果需要）
- 如果AI决定需要搜索，会调用 `CourseSearchTool`
- 工具执行以下步骤：
  - 调用 `vector_store.search()`
  - 解析课程名称（如果提供）
  - 构建ChromaDB过滤条件
  - 执行语义搜索
  - 格式化搜索结果

### 6. 向量存储搜索详细流程
- **课程名称解析**：使用向量搜索找到最佳匹配的课程
- **过滤条件构建**：根据课程名称和课程编号构建ChromaDB过滤器
- **语义搜索**：在 `course_content` 集合中执行向量搜索
- **结果格式化**：将搜索结果格式化为可读文本

### 7. 最终响应生成
- AI基于搜索结果（如果有）生成最终响应
- 更新会话历史记录
- 返回包含答案、来源和会话ID的响应

### 8. 响应返回
- 返回 `QueryResponse` 对象
- 包含：
  - `answer`：AI生成的答案
  - `sources`：搜索结果的来源信息
  - `session_id`：会话标识符

## 关键组件说明

- **RAGSystem**：主要协调器，管理所有组件
- **VectorStore**：使用ChromaDB进行向量存储和搜索
- **AIGenerator**：与Claude API交互，生成响应
- **SessionManager**：管理对话会话和历史
- **ToolManager**：管理可用的搜索工具
- **CourseSearchTool**：具体的课程内容搜索工具
