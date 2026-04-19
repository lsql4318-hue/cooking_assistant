import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import GraphView from '../views/GraphView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import QAView from '../views/QAView.vue'
import ServiceView from '../views/ServiceView.vue'
import CommunityView from '../views/CommunityView.vue'
import ProfileView from '../views/ProfileView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/graph',
      name: 'graph',
      component: GraphView,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
    },
    {
      path: '/qa',
      name: 'qa',
      component: QAView,
    },
    {
      path: '/service',
      name: 'service',
      component: ServiceView,
    },
    {
      path: '/community',
      name: 'community',
      component: CommunityView,
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
    },
    {
      path: '/recipes',
      name: 'recipes',
      component: () => import('../views/RecipeListView.vue')
    },
    {
      path: '/recipe/:id',
      name: 'recipe-detail',
      component: () => import('../views/RecipeDetailView.vue')
    },
    {
      path: '/publish',
      name: 'publish',
      component: () => import('../views/PublishRecipeView.vue')
    },
    {
      path: '/personal',
      name: 'personal',
      component: () => import('../views/PersonalServiceView.vue')
    },
    {
      path: '/submission/edit/:id',
      name: 'submission-edit',
      component: () => import('../views/EditSubmissionView.vue')
    }
  ],
})

export default router