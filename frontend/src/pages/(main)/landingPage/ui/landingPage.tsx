import { Button } from "@/shared/ui/button";
import { useNavigate } from "react-router-dom";
import { ERouteNames } from "@/shared/lib/routeVariables";
import { useGetProfileQuery } from "@/entities/auth/hooks/useGetProfile";
import { getAccessToken } from "@/entities/token/lib/tokenService";
import { useMemo } from "react";
import { motion } from "framer-motion";
import { Image } from "@/shared/ui/image/image";
import { Icon, IconTypes } from "@/shared/ui/icon";
import {
  containerVariants,
  itemVariants,
  cardVariants,
  benefits,
} from "../lib/constants";

const LandingPage = () => {
  const navigate = useNavigate();
  const token = getAccessToken();
  const { data: profileData, isSuccess: isProfileSuccess } =
    useGetProfileQuery(false);
  const isAuthenticated = useMemo(() => {
    return !!token && isProfileSuccess && !!profileData;
  }, [token, isProfileSuccess, profileData]);

  const handleStartWork = () => {
    if (isAuthenticated) {
      navigate(`/${ERouteNames.DASHBOARD_ROUTE}`);
    } else {
      navigate(`/${ERouteNames.AUTH_ROUTE}/${ERouteNames.REGISTER_ROUTE}`);
    }
  };

  const bannerSections = [
    {
      image: "/images/PurePromo-2.webp",
      title: "Сервис доступен 24 на 7",
      description:
        "Только представьте — ваша личная команда специалистов, которые любят сверхурочную работу. Они всегда готовы сэкономить ваш самый ценный ресурс — время",
      textPosition: "right" as const,
    },
    {
      image: "/images/PurePromo-3.webp",
      title: "Больше не нужно заниматься поиском специалистов",
      description: "Умный ассистент поможет решить задачу",
      textPosition: "left" as const,
    },
  ];

  const benefitCards = [
    {
      title: "Сэкономьте на экспертах",
      description: "Каждая задача решается на уровне профессионала",
    },
    {
      title: "Ускорьте процессы",
      description: "От запроса до готового решения за считанные минуты",
    },
    {
      title: "Сократите операционку",
      description:
        "Просто опишите задачу своими словами — нейросеть выдаст наилучший результат",
    },
  ];

  return (
    <div className="flex min-h-screen w-full flex-col bg-black overflow-hidden">
      <section className="relative min-h-screen flex flex-col">
        <div className="absolute inset-0 bg-gradient-to-b from-gray-900 via-black to-black" />

        <div className="container mx-auto px-4 sm:px-6 lg:px-28 pt-12 sm:pt-16 lg:pt-20 pb-6 sm:pb-8 relative z-10">
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="flex flex-col items-center justify-center mb-12 sm:mb-16"
          >
            <motion.div
              variants={itemVariants}
              className="flex items-center gap-3 sm:gap-4 mb-4"
            >
              <motion.div
                className="group cursor-pointer rounded-lg transition-all duration-300 p-2"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
              >
                <Icon
                  type={IconTypes.LOGO_OUTLINED_V2}
                  className="text-4xl sm:text-5xl lg:text-6xl text-red-400 transition-all duration-300 group-hover:scale-110 group-hover:text-red-600 group-hover:drop-shadow-lg"
                />
              </motion.div>
              <motion.h1
                variants={itemVariants}
                className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold text-white"
              >
                FinAi
              </motion.h1>
            </motion.div>
            <motion.p
              variants={itemVariants}
              className="text-gray-300 text-sm sm:text-base md:text-lg text-center max-w-2xl"
            >
              Ваш персональный AI ассистент для бизнеса
            </motion.p>
          </motion.div>

          <motion.div
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 mb-8 sm:mb-12"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            {benefitCards.map((card, index) => (
              <motion.div
                key={index}
                variants={itemVariants}
                className="rounded-2xl sm:rounded-3xl bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 p-4 sm:p-6 lg:p-8 hover:bg-gray-800/70 transition-all"
              >
                <h3 className="text-white font-semibold text-base sm:text-lg mb-2">
                  {card.title}
                </h3>
                <p className="text-gray-300 text-xs sm:text-sm leading-relaxed">
                  {card.description}
                </p>
              </motion.div>
            ))}
          </motion.div>
        </div>

        <motion.div
          className="flex-1 relative z-10"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
        >
          <div className="bg-white dark:bg-gray-900 rounded-t-[2rem] sm:rounded-t-[3rem] md:rounded-t-[4rem] min-h-[60vh] pt-8 sm:pt-12 pb-12 sm:pb-20">
            <div className="container mx-auto px-4 sm:px-6 lg:px-8">
              <motion.div
                variants={containerVariants}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                className="text-center mb-8 sm:mb-12 lg:mb-16"
              >
                <motion.h1
                  variants={itemVariants}
                  className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl font-bold text-gray-900 dark:text-white mb-4 sm:mb-6 leading-tight px-2"
                >
                  Ваша виртуальная команда
                </motion.h1>
                <motion.p
                  variants={itemVariants}
                  className="text-base sm:text-lg md:text-xl lg:text-2xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto mb-6 sm:mb-8 px-4"
                >
                  AI Copilot для микробизнеса — решайте задачи быстрее,
                  принимайте решения эффективнее
                </motion.p>
                <motion.div
                  variants={itemVariants}
                  className="flex flex-col sm:flex-row justify-center items-center gap-3 sm:gap-4 px-4"
                >
                  <Button
                    onClick={handleStartWork}
                    className="w-full sm:w-auto rounded-2xl bg-red-600 hover:bg-red-700 text-white px-6 sm:px-8 lg:px-10 py-5 sm:py-6 lg:py-7 text-base sm:text-lg font-semibold shadow-lg shadow-red-600/30"
                  >
                    Начать работу
                  </Button>
                  {!isAuthenticated && (
                    <Button
                      variant="outline"
                      onClick={() => navigate(`/${ERouteNames.AUTH_ROUTE}`)}
                      className="w-full sm:w-auto rounded-2xl border-2 border-gray-300 dark:border-gray-600 px-6 sm:px-8 lg:px-10 py-5 sm:py-6 lg:py-7 text-base sm:text-lg"
                    >
                      Войти
                    </Button>
                  )}
                </motion.div>
              </motion.div>

              <motion.div
                className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-12 sm:mb-16 lg:mb-20 px-4 sm:px-8 lg:px-12 xl:px-20"
                variants={containerVariants}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, amount: 0.2 }}
              >
                {benefits.slice(0, 4).map((benefit, index) => (
                  <motion.div
                    key={index}
                    variants={cardVariants}
                    whileHover="hover"
                    className="rounded-2xl sm:rounded-3xl bg-gray-50 dark:bg-gray-800/50 p-6 sm:p-8 lg:p-10 border border-gray-200 dark:border-gray-700 hover:border-red-500/50 transition-all"
                  >
                    <p className="text-sm sm:text-base text-gray-900 dark:text-gray-100 font-medium text-center">
                      {benefit}
                    </p>
                  </motion.div>
                ))}
              </motion.div>

              <motion.div
                className="rounded-2xl sm:rounded-3xl bg-gray-50 mx-4 sm:mx-8 lg:mx-12 xl:mx-20 dark:bg-gray-800/50 p-6 sm:p-8 md:p-10 lg:p-14 mb-12 sm:mb-16 lg:mb-20 border border-gray-200 dark:border-gray-700"
                variants={containerVariants}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
              >
                <motion.div
                  variants={itemVariants}
                  className="mb-8 sm:mb-10 lg:mb-12 text-center"
                >
                  <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4 sm:mb-6 px-4">
                    Почему выбирают нас
                  </h2>
                  <p className="text-sm sm:text-base lg:text-lg text-gray-600 dark:text-gray-300 max-w-3xl mx-auto px-4">
                    AI Copilot помогает представителям микробизнеса решать
                    задачи быстрее и эффективнее, предоставляя качественные
                    ответы на любые вопросы прямо в мессенджере или мобильном
                    приложении.
                  </p>
                </motion.div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
                  {benefits.map((benefit, index) => (
                    <motion.div
                      key={index}
                      variants={itemVariants}
                      className="rounded-xl sm:rounded-2xl bg-white dark:bg-gray-900/50 p-4 sm:p-6 border border-gray-200 dark:border-gray-700 hover:border-red-500/50 transition-all"
                    >
                      <p className="text-sm sm:text-base font-medium text-gray-900 dark:text-gray-100 text-center">
                        {benefit}
                      </p>
                    </motion.div>
                  ))}
                </div>
              </motion.div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-10 lg:gap-14 px-4 sm:px-8 lg:px-12 xl:px-20 md:mb-16 mb-8">
                {bannerSections.map((banner, index) => (
                  <motion.div
                    key={index}
                    whileHover={{ y: -5 }}
                    transition={{ type: "spring", stiffness: 120 }}
                    className="flex flex-col overflow-hidden rounded-3xl shadow-2xl bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border border-gray-200/30 dark:border-gray-700/30 hover:shadow-3xl transition-all"
                  >
                    <div className="relative h-48 sm:h-56 lg:h-64 w-full overflow-hidden">
                      <Image
                        src={banner.image}
                        alt={banner.title}
                        className="object-cover w-full h-full transition-transform duration-700 hover:scale-105"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-black/10 to-transparent" />
                      <div className="absolute bottom-4 left-4 right-4">
                        <h2 className="text-xl sm:text-2xl lg:text-3xl font-bold text-white drop-shadow-md">
                          {banner.title}
                        </h2>
                      </div>
                    </div>

                    <div className="flex flex-col justify-between p-6 sm:p-8 space-y-4">
                      <p className="text-gray-700 dark:text-gray-300 text-sm sm:text-base leading-relaxed">
                        {banner.description}
                      </p>

                      <div className="flex items-center justify-between">
                        <div className="h-1 w-12 bg-gradient-to-r from-red-500 to-pink-600 rounded-full" />
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          className="text-sm font-medium text-pink-600 hover:text-pink-700 dark:text-pink-400 dark:hover:text-pink-300"
                        >
                          Подробнее →
                        </motion.button>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>

              <motion.div
                variants={containerVariants}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, amount: 0.3 }}
              >
                <motion.div
                  variants={itemVariants}
                  className="rounded-2xl sm:rounded-3xl bg-gradient-to-br mx-4 sm:mx-8 lg:mx-12 xl:mx-20 from-red-600 to-pink-600 p-6 sm:p-8 md:p-12 lg:p-16 text-center shadow-2xl relative overflow-hidden"
                >
                  <div className="relative z-10">
                    <motion.h2
                      variants={itemVariants}
                      className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-3 sm:mb-4 px-4"
                    >
                      Готовы начать?
                    </motion.h2>
                    <motion.p
                      variants={itemVariants}
                      className="text-white/90 mb-6 sm:mb-8 max-w-2xl mx-auto text-sm sm:text-base lg:text-lg px-4"
                    >
                      Присоединяйтесь к тысячам пользователей, которые уже
                      используют AI Copilot для развития своего бизнеса
                    </motion.p>
                    <motion.div
                      variants={itemVariants}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <Button
                        onClick={handleStartWork}
                        className="rounded-2xl bg-white text-red-600 hover:bg-white/90 shadow-xl px-6 sm:px-8 lg:px-10 py-5 sm:py-6 lg:py-7 text-base sm:text-lg font-semibold"
                      >
                        Начать бесплатно
                      </Button>
                    </motion.div>
                  </div>
                </motion.div>
              </motion.div>
            </div>
          </div>
        </motion.div>
      </section>
    </div>
  );
};

export default LandingPage;
