import { Router } from "express";
import { signupUser  , loginUser , getUserProfile} from "../Controllers/user.controller.js";
import authMiddleware from "../Middleware/authMiddleware.js";
const router = Router();
router.route("/adduser").post(signupUser)
router.route("/loginuser").post(loginUser)
router.get('/profile', authMiddleware, getUserProfile);

export default router;