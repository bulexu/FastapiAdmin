import request from "@/utils/request";
import { Auth } from "@/utils/auth";
import { fetchEventSource } from "@microsoft/fetch-event-source";

const API_PATH = "/application/prompt";

function streamRequest(url: string, data: any, onMessage: (event: any) => void, onclose: () => void, onError: () => void) {
  const accessToken = Auth.getAccessToken();
  const fullUrl = import.meta.env.VITE_APP_BASE_API + url;

  fetchEventSource(fullUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': accessToken ? 'Bearer ' + accessToken : ''
    },
    body: JSON.stringify(data),
    openWhenHidden: true,
    onmessage(event) {
      if (event.data === '[DONE]') {
        onclose();
        return;
      }
      onMessage(event);
    },
    onclose() {
      onclose();
    },
    onerror(err) {
      onError();
      throw err; // Prevent retry
    }
  });
}

const PromptAPI = {
  getPage(query: PromptPageQuery) {
    return request<ApiResponse<PageResult<PromptTable[]>>>({
      url: `${API_PATH}/page`,
      method: "get",
      params: query,
    });
  },

  getDetail(id: number) {
    return request<ApiResponse<PromptTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  create(body: PromptForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  update(id: number, body: PromptForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  delete(body: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: body,
    });
  },

  getVersionList(promptId: number) {
    return request<ApiResponse<PromptVersionTable[]>>({
      url: `${API_PATH}/${promptId}/versions`,
      method: "get",
    });
  },

  rollbackVersion(promptId: number, versionId: number) {
    return request<ApiResponse>({
      url: `${API_PATH}/rollback/${promptId}/${versionId}`,
      method: "post",
    });
  },

  pushToProduction(id: number) {
    return request<ApiResponse>({
      url: `${API_PATH}/push/${id}`,
      method: "post",
    });
  },

  evaluatePrompt(body: { prompt: string }) {
    return request<ApiResponse>({
      url: `${API_PATH}/evaluate`,
      method: "post",
      data: body,
    });
  },
  optimizePromptWithSuggestions(data: any, onMessage: (res: any) => void, onclose: () => void, onError: () => void) {
      const payload = {
          model: data.model,
          original_content: data.content,
          suggestions: data.suggestions
      };
      streamRequest(`${API_PATH}/optimize`, payload, onMessage, onclose, onError);
  }
};

export default PromptAPI;

export interface PromptPageQuery extends PageQuery {
  prompt_title?: string;
  prompt_code?: string;
  is_publish?: number;
  created_time?: string[];
  updated_time?: string[];
  created_id?: number;
  updated_id?: number;
}

export interface PromptTable extends BaseType {
  prompt_code?: string;
  prompt_title?: string;
  content?: string;
  ability_tags?: string[];
  instructions?: string[];
  evaluate_result?: any;
  is_publish?: number;
  version_id?: number;
  created_by?: creatorType;
  updated_by?: updatorType;
}

export interface PromptVersionTable extends BaseType {
  prompt_id?: number;
  version?: number;
  content?: string;
  ability_tags?: string[];
  instructions?: string[];
  is_archived?: number;
}

export interface PromptForm extends BaseFormType {
  prompt_code?: string;
  prompt_title?: string;
  content?: string;
  ability_tags?: string[];
  instructions?: string[];
  description?: string;
}
