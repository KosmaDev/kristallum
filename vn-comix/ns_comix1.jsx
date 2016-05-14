//@include "../scripts/photoshop/libs/comixgen.jsx"
var globals = {};
initComix("d:/Downloads/comix_pages", globals);

//================ INTRO ============================
switchScene("bgs","logo");
switchScene("bgs_mods_up",null);
switchScene("bgs_mods_down",null);
switchScene("text_shade",null);
switchScene("chars",null);
say("texts",null,null);
switchScene("text_shade","main_tbg");
//================ LINES ===============================
switchScene("bgs","nks_hall2_mlb");
switchScene("bgs_mods_up","record_mode_on");
switchScene("chars","r_ja_lau_spok",["texts","r"]);
say(null,null,"Приветствую!");
switchScene("chars","r_ja_smi");
say(null,null,"Будьте как дома, но не забывайте, что вы в гостях.");
say(null,null,"Сегодня у меня юбилей. Это десятый выпуск моего видеоблога...");
switchScene("chars","r_ja_lau_spok");
switchScene("bgs_mods_down","papsh_logo");
say(null,null,"\"В гостях у инопланетянки.\"");
switchScene("chars","r_ja_smi");
say(null,null,"Поэтому начну его с ответов на...");
switchScene("bgs_mods_down","papsh_faq");
say(null,null,"Самые частые вопросы.");
say(null,null,"Я почитала ваши комментарии...");
say(null,null,"К прошлым видео.");
switchScene("chars","r_ja_smi2");
say(null,null,"И пришла к выводу, что вам надо поработать над грамотностью.");
switchScene("bgs_mods_down","papsh_ashipki");
switchScene("chars","r_ja_smi");
say(null,null,"Поэтому вопросы, написанные с \"ашипками\", проигнорированы.");
say(null,null,"А их авторы отправились в бан.");
switchScene("chars","r_ja_smi2");
say(null,null,"Извините.");
switchScene("chars","r_ja_smi");
switchScene("bgs_mods_down",null);
say(null,null,"Первый вопрос.");
say(null,null,"\"Как вы докатились до жизни такой?\" зачеркнуто... видеоблогинга?");
switchScene("chars","r_ja_smi2");
say(null,null,"Эту идею мне предложил один знакомый.");
say(null,null,"Как-то мы спорили, и он сказал:");
switchScene("chars","r_ja_smi3");
say("texts","c3","Why so serious?");
say("texts","c3","Забудь свои правила! Будь проще!");
say("texts","c3","Иди, узнай как живые люди разговаривают!");
say(null,null,"Вот я и узнала.");
switchScene("chars","r_ja_smi");
say(null,null,"Тем более, ночью мне все равно делать нечего.");
switchScene("chars","r_ja_smi2");
switchScene("bgs_mods_down","papsh_logo");
say(null,null,"Вопрос: почему такое странное название канала?");
switchScene("chars","r_ja_smi");
say(null,null,"Технически, я с другой планеты - поэтому инопланетянка.");
switchScene("chars","r_ja_smi2");
switchScene("bgs_mods_down",null);
say(null,null,"Вопрос: а вам говорили, что в этих очках вы похожи на мицгел?");
switchScene("chars","r_ja_smi");
say(null,null,"Во-первых, кто такая мицгел?");
switchScene("bgs_mods_down","papsh_mitsgirl");
say(null,null,"Я тут поискала в интернетах и могу сказать...");
say(null,null,"Что я не вижу ничего общего.");
say(null,null,"У нее вообще глаза желтые. Как у моей знакомой, лол.");
switchScene("bgs_mods_down",null);
switchScene("chars","r_ja_smi2");
say(null,null,"Вопрос: я ваш большой фанат и давно хотел спросить а чем вы увлекаитесь?");
say(null,null,"Во-первых, в вопросе были допущены ошибки и не хватает запятых...");
switchScene("chars","r_ja_smi");
say(null,null,"Поэтому автор отправился в бан.");
switchScene("chars","r_ja_sad2");
say(null,null,"Но вопрос... очень часто встречается, поэтому отвечу.");
switchScene("bgs_mods_down","papsh_books");
switchScene("chars","r_ja_smi3");
say(null,null,"Я люблю читать, особенно фантастику.");
say(null,null,"Интересуюсь историей и... и разными игрушками.");
switchScene("bgs","nks_hall2");
switchScene("bgs_mods_down","molbfalll1");
say("texts",null, null);
switchScene("bgs_mods_down","molbfalll2");
switchScene("chars","r_ja_sad2");
say(null,null,"Ой!");
switchScene("chars",null);
say(null,null,"Простите за накладку.");
switchScene("bgs_mods_down",null);
switchScene("chars","r_ja_nnnear");
say(null,null,"У нас в студии что-то сломалось.");
say(null,null,"Пишите свои комментарии и предложения на следующий раз.");
say(null,null,"Как обычно, под этим видео.");
switchScene("chars","r_ja_lau_spok");
say(null,null,"Спокеда!");
switchScene("chars",null);
//======================================================
//switchScene("bgs_mods_up","menu");
//say("texts",null, null);
//====================
alert("Done!");
