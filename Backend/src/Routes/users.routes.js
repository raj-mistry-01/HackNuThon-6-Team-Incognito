import { Router } from "express";
import { signupUser } from "../Controllers/user.controller.js";
const router = Router();
router.route("/adduser").post(signupUser)
export default router;