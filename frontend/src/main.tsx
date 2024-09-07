import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import {
  createBrowserRouter,
  createRoutesFromElements,
  Route,
  RouterProvider,
} from 'react-router-dom';
import Root, {
  loader as rootLoader,
  action as rootAction,
} from './routes/root';
import Index from './routes/index';
import Contact, {
  loader as contactLoader,
  action as contactAction,
} from './routes/contact';
import EditContact, { action as editAction } from './routes/edit';
import { action as destroyAction } from './routes/destroy';
import ErrorPage from './error-page';
import { AuthContextProvider } from './auth';
import Login from './routes/login';
import Guard from './routes/guard';

const router = createBrowserRouter(
  createRoutesFromElements(
    <Route>
      <Route element={<Guard />} errorElement={<ErrorPage />}>
        <Route
          path="/"
          element={<Root />}
          loader={rootLoader}
          action={rootAction}
        >
          <Route errorElement={<ErrorPage />}>
            <Route index element={<Index />} />
            <Route
              path="contacts/:contactId"
              element={<Contact />}
              loader={contactLoader}
              action={contactAction}
            />
            <Route
              path="contacts/:contactId/edit"
              element={<EditContact />}
              loader={contactLoader}
              action={editAction}
            />
            <Route path="contacts/:contactId/destroy" action={destroyAction} />
          </Route>
        </Route>
      </Route>
      <Route path="/login" element={<Login />} />
    </Route>
  )
);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthContextProvider>
      <RouterProvider router={router} />
    </AuthContextProvider>
  </StrictMode>
);
