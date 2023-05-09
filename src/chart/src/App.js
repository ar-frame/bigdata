import Chart from './Chart'
import Shipan from './Shipan'
import { BrowserRouter, Routes, Route } from "react-router-dom"
import { Outlet, Link } from "react-router-dom"

const Home = () => {
  return <h1>KT开源量化软件</h1>;
};
const NoPage = () => {
  return <h1>404</h1>;
}
const Layout = () => {
  return (
    <>
      <Outlet />
    </>
  )
}

export default function App(props) {
  return (

    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="shipan" element={<Shipan />} />
          <Route path="paint" element={<Chart />} />
          <Route path="*" element={<NoPage />} />
        </Route>
      </Routes>
    </BrowserRouter>

  )
}