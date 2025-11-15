import api from "../axios";

export const getCourses = async (page = 1, perPage = 20) => {
  const response = await api.get(`/courses?page=${page}&per_page=${perPage}`);
  return response.data;
};

export const getCourse = async (id: number) => {
  const response = await api.get(`/courses/${id}`);
  return response.data;
};
