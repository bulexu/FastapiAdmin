import request from '@/utils/request';

const API_PATH = "/dataset/dataset";

// 数据集API
export default {
  // 获取数据集表列表
  getDatasetTableList(params?: any) {
    return request<ApiResponse>({
      url: `${API_PATH}/list`,
      method: 'get',
      params
    });
  },

  // 获取数据集表详情（列信息）
  getDatasetTableDetail(tableId: number) {
    return request<ApiResponse>({
      url: `${API_PATH}/${tableId}`,
      method: 'get'
    });
  },

  // 获取数据集表数据
  getDatasetTableData(tableId: number, params?: any) {
    return request<ApiResponse>({
      url: `${API_PATH}/${tableId}/data`,
      method: 'get',
      params
    });
  },

  // 导出数据集表数据
  exportDatasetTableData(tableId: number, params?: any) {
    return request<Blob>({
      url: `${API_PATH}/${tableId}/export`,
      method: 'get',
      params,
      responseType: 'blob'
    });
  }
};
