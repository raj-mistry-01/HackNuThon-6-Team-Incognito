import  express from 'express';
import cors from "cors";
import cookieParser from "cookie-parser";
import testRouter from "./Routes/expr.routes.js"
import userRouter from "./Routes/users.routes.js"
import processRouter from "./Routes/process.routes.js"
import projectRouter from "./Routes/project.routes.js"
import reponseRouter from "./Routes/response.routes.js"
const app = express();

app.use(
  cors({
    origin: "https://incognito-three-chi.vercel.app", 
  })
);

app.use(express.json({ limit: "16kb" }));
app.use(express.urlencoded({ extended: true, limit: "16kb" }));
app.use(express.static("public"));
app.use(cookieParser());
app.use(express.json());

app.use("/api/test1/exprs" , testRouter)
app.use("/api/users" , userRouter)
app.use("/api/process" , processRouter)
app.use("/api/project" , projectRouter)
app.use("/api/resp" , reponseRouter)
app.get("/api/testing", (req, res) => {
  return res.json({"ok" : "ok"})
});


export {app}
