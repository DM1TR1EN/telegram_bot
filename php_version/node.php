<?php

// header('Content-Type: text/html; charset=utf-8');
// подрубаем API
// require_once("vendor/autoload.php");
require_once "vendor/autoload.php";
require_once "CodesGetter.php";

// if(true){
// 	error_reporting(E_ALL & ~(E_NOTICE | E_USER_NOTICE | E_DEPRECATED));
// 	ini_set('display_errors', 1);
// }

// создаем переменную бота
// $tg_bot_api_token = "";

// https://t.me/suremasu_bot
$tg_bot_api_token = "";

// https://t.me/new_suremasu_bot
// $tg_bot_api_token = "";

// $bot = new \TelegramBot\Api\BotApi($tg_bot_api_token);
$bot = new \TelegramBot\Api\Client($tg_bot_api_token);

// $bot->sendMessage(178188001, "Я жив");

try {

    // Handle /ping command
    $bot->command('ping', function ($message) use ($bot) {
        $bot->sendMessage($message->getChat()->getId(), 'pong!');
    });
    
    // Обрабатываем стартовое сообщение /start
    $bot->command('start', function ($message) use ($bot) {
        $user_id         = $message->getChat()->getId();
        
        $welcome_msg = "Good day, commander! Choose a language:\n\nПриветствуем! Выберите язык:";
        // Клава подстраивает высоту под кол-во кнопок. НЕ исчезает после нажатия
        $reply_keyboard_leng = new \TelegramBot\Api\Types\ReplyKeyboardMarkup([['🇷🇺 РУССКИЙ'], ['🇬🇧 ENGLISH']], null, true);
        // $bot->sendMessage($user_id, "Welcome!\nПривет!",false, null, null, $reply_keyboard_leng);
        $bot->sendMessage($user_id, $welcome_msg,false, null, null, $reply_keyboard_leng);
    });

    // Обрабатываем текстовые сообщения-ответы пользователя, поступающие от reply клавиатуры
    $bot->on(function (\TelegramBot\Api\Types\Update $update) use ($bot) {
        // Проверяем, является ли сообщение отредактированным и игнорируем его
        if ($update->getEditedMessage()) {
            return;
        }

        $message        = $update->getMessage();
        $message_text   = $message->getText();
        $user_id        = $message->getChat()->getId();
        // $info_key_ru    = '❓ Информация';
        // $info_key_en    = '❓ Info';
        
        // Массив с надписями для кнопок reply клавиатуры
        $info_key = [
            "ru" => '❓ Информация',
            "en" => '❓ Info',
        ];
        $demo_key = [
            "ru" => '🔧 Получить демо доступ',
            "en" => '🔧 I need demo access',
        ];
        
        // Обрабатываем поступившее сообщение с выбранным языком
        if(strcasecmp($message_text, '🇷🇺 РУССКИЙ') == 0)   // Бинарно-безопасное сравнение строк без учёта регистра
        {
            $info_msg_text = 'Это сервис по предоставлению демо доступа к индикатору `Trend Breaking Level` (для TradingView)!';
            
            // Создаём не исчезающую клавиатуру с двумя рядами кнопок
            $reply_keyboard = new \TelegramBot\Api\Types\ReplyKeyboardMarkup([[$demo_key['ru']], [$info_key['ru']]], null, true);
            
            $bot->sendMessage($user_id, $info_msg_text, false, null, null, $reply_keyboard);
            // $bot->sendMessage($user_id, 'Добро пожаловать!', false, null, null, $reply_keyboard);
        }
        else if(strcasecmp($message_text, '🇬🇧 ENGLISH') == 0)
        {
            $info_msg_text = 'This is a service for providing demo access to `Trend Breaking Level` indicator (for TradingView)!';
            
            // Создаём не исчезающую клавиатуру с двумя рядами кнопок
            $reply_keyboard = new \TelegramBot\Api\Types\ReplyKeyboardMarkup([[$demo_key['en']], [$info_key['en']]], null, true);
            
            $bot->sendMessage($user_id, $info_msg_text, false, null, null, $reply_keyboard);
            // $bot->sendMessage($user_id, 'Good day, commander!', false, null, null, $reply_keyboard);
        }
        
        // Обрабатываем поступившее сообщение '❓ Информация'
        
        // Объявляем набор ссылок
        $overview_url   = 'https://www.tradingview.com/chart/CL1!/WpLFZtrb-Demonstration-of-the-indicator-Trend-Breaking-Level-TBL/';
        $tg_channel_url = 'https://t.me/suremasu';
        $website_url    = 'https://surema.su';
        
        // if(strcasecmp($message_text, '❓ Информация') == 0) 
        if(strcasecmp($message_text, $info_key['ru']) == 0)
        {
            $info_msg_text = 'Немного полезной информации:';
            // $info_msg_text = 'Это сервис по предоставлению демо доступа к TradingView-индикатору Trend Breaking Level (TBL)!';
            $inline_keyboard = new \TelegramBot\Api\Types\Inline\InlineKeyboardMarkup(
                    [
                        [
                            ['text' => 'Обзор индикатора на графике', 'url' => $overview_url]
                        ],
                        [
                            ['text' => 'Руководство по использованию', 'url' => $website_url]
                        ],
                        [
                            ['text' => 'ДОСТУП К ПОЛНОЙ ВЕРСИИ', 'url' => $tg_channel_url]
                        ]
                    ]
                );
            $bot->sendMessage($user_id, $info_msg_text , null, false, null, $inline_keyboard);
        }
        // else if(strcasecmp($message_text, '❓ Info' )== 0)   
        else if(strcasecmp($message_text, $info_key['en']) == 0)
        {
            $info_msg_text = 'Some useful information:';
            // $info_msg_text = 'This is a service for providing demo access to Trend Breaking Level (TBL) indicator (for TradingView)!';
            $inline_keyboard = new \TelegramBot\Api\Types\Inline\InlineKeyboardMarkup(
                    [
                        [
                            ['text' => 'Overview the indicator on the chart', 'url' => $overview_url]
                        ],
                        [
                            ['text' => 'User manual', 'url' => $website_url]
                        ],
                        [
                            ['text' => 'GET FULL VERSION', 'url' => $tg_channel_url]
                        ]
                    ]
                );
            $bot->sendMessage($user_id, $info_msg_text , null, false, null, $inline_keyboard);
        }
        
        // Обрабатываем поступившее сообщение '🔧 Получить демо доступ' 
        
        // Определяем ссылку на демо версию индикатора
        $demo_indicator_url = 'https://www.tradingview.com/script/4QoynGNS-demo-Trend-Breaking-Level-TBL/';

        // if(strcasecmp($message_text, '🔧 Получить демо доступ') == 0) 
        if(strcasecmp($message_text, $demo_key['ru']) == 0) 
        {
            // Задаём айди группы, принадлежность к которому проверяем. (строка или int). Имя можно в формате: @channelusername
            // $target_group_id = '-1001845418299';                             
            $target_group_id = '@suremasu';
            
            // Получаем статус юзера по отношению к $target_group_id
            // NOTE: Существующие статусы юзера: “creator”, “administrator”, “member”, “restricted”, “left” or “kicked”
            $user_status = $bot->getChatMember($target_group_id, $user_id)->getStatus(); 
            
            // Cтатус юзера должен быть как минимум member, т.к. админы не в счёт
            if (strcasecmp($user_status, 'creator') == 0 || strcasecmp($user_status, 'member') == 0)
            {
                if (!checkUser($user_id))
                {
                    // Получение код из БД
                    $ver_code   =   getVrfCode();

                    // Формирование кнопки с ссылкой
                    $inline_keyboard = new \TelegramBot\Api\Types\Inline\InlineKeyboardMarkup(
                            [
                                [
                                    ['text' => 'Добавить индикатор на график', 'url' => $demo_indicator_url]
                                ]
                            ]
                        );
                    // Отправляем сообщение пользователю
                    $bot->sendMessage($user_id, 'Держи ключ демо доступа на 3 дня: ');
                    
                    //Ключ доступа отправляется в этом сообщении:
                    $bot->sendMessage($user_id, $ver_code, null, false, null, $inline_keyboard); 
                    // $bot->sendMessage($user_id, 'Добавь индикатор на график и введи ключ', null, false, null, $reply_keyboard);
                }
                else
                {
                    $info_msg_text_ = 'Ты уже получал демо доступ!';
                    $inline_keyboard = new \TelegramBot\Api\Types\Inline\InlineKeyboardMarkup(
                            [
                                [
                                    ['text' => 'Оформи подписку на полную версию', 'url' => $tg_channel_url]
                                ]
                            ]
                        );
                    $bot->sendMessage($user_id, $info_msg_text_ , null, false, null, $inline_keyboard);
                    // $bot->sendMessage($user_id, 'Ты уже получил свой код. Покупай полный доступ!');
                }
                // ——D—E—B—U—G———S—E—C—T—I—O—N——
                // $bot->sendMessage($user_id, 'You are: '.$res->getStatus());
            }
            else
            {
                // $bot->sendMessage($user_id, 'Сначала подпишись на наш канал https://t.me/bbcdfgg и попробуй снова!');
                $bot->sendMessage($user_id, 'Сначала подпишись на наш канал @suremasu и попробуй снова!');

                // $reply_keyboard = new \TelegramBot\Api\Types\Inline\InlineKeyboardMarkup(
                //         [
                //             [
                //                 ['text' => '@bbcdfgg', 'url' => 'https://t.me/bbcdfgg']
                //             ]
                //         ]
                //     );
                // $bot->sendMessage($user_id, 'Сначала подпишись на наш канал и попробуй снова!', null, false, null, $reply_keyboard);
            }
        }
        else if(strcasecmp($message_text, $demo_key['en']) == 0) 
        {
            // Задаём айди группы, принадлежность к которому проверяем. (строка или int). Имя можно в формате: @channelusername
            // $target_group_id = '-1001845418299';                             
            $target_group_id = '@suremasu';
            
            // Получаем статус юзера по отношению к $target_group_id
            // NOTE: Существующие статусы юзера: “creator”, “administrator”, “member”, “restricted”, “left” or “kicked”
            $user_status = $bot->getChatMember($target_group_id, $user_id)->getStatus(); 
            
            // Cтатус юзера должен быть как минимум member, т.к. админы не в счёт
            if (strcasecmp($user_status, 'creator') == 0 || strcasecmp($user_status, 'member') == 0)
            {
                if (!checkUser($user_id))
                {
                    // Получение код из БД
                    $ver_code   =   getVrfCode();

                    // Формирование кнопки с ссылкой
                    $inline_keyboard = new \TelegramBot\Api\Types\Inline\InlineKeyboardMarkup(
                            [
                                [
                                    ['text' => 'Add indicator to the chart', 'url' => $demo_indicator_url]
                                ]
                            ]
                        );
                    // Отправляем сообщение пользователю
                    $bot->sendMessage($user_id, 'Take the demo access code for 3 days: ');
                    //Ключ доступа отправляется в этом сообщении:
                    $bot->sendMessage($user_id, $ver_code, null, false, null, $inline_keyboard); 
                    // $bot->sendMessage($user_id, 'Добавь индикатор на график и введи ключ', null, false, null, $reply_keyboard);
                }
                else
                    $info_msg_text_ = 'You have already get demo access!';
                    $inline_keyboard = new \TelegramBot\Api\Types\Inline\InlineKeyboardMarkup(
                            [
                                [
                                    ['text' => 'Subscribe to full version', 'url' => $tg_channel_url]
                                ]
                            ]
                        );
                    $bot->sendMessage($user_id, $info_msg_text_ , null, false, null, $inline_keyboard);
                    // $bot->sendMessage($user_id, 'You have already received your code. Buy full access!');
                
                // ——D—E—B—U—G———S—E—C—T—I—O—N——
                // $bot->sendMessage($user_id, 'You are: '.$res->getStatus());
            }
            else
            {
                // $bot->sendMessage($user_id, 'Сначала подпишись на наш канал https://t.me/bbcdfgg и попробуй снова!');
                $bot->sendMessage($user_id, 'First subscribe to our @suremasu channel and try again!');
                
                // $reply_keyboard = new \TelegramBot\Api\Types\Inline\InlineKeyboardMarkup(
                //         [
                //             [
                //                 ['text' => '@bbcdfgg', 'url' => 'https://t.me/bbcdfgg']
                //             ]
                //         ]
                //     );
                // $bot->sendMessage($user_id, 'Сначала подпишись на наш канал и попробуй снова!', null, false, null, $reply_keyboard);
            }
        }
        
        // ——D—E—B—U—G———S—E—C—T—I—O—N——
        if(strcasecmp($message_text, '031213') == 0)
        {
            $reply_keyboard = new \TelegramBot\Api\Types\ReplyKeyboardMarkup([['❓ Информация'], ['🔧 Получить демо доступ']], null, true);
            if (ClearUserDb() != null)
    	   	    $bot->sendMessage($user_id, "Файл users_db успешно очищен!", false, null, null, $reply_keyboard);
	   	    else
    	   	    $bot->sendMessage($user_id, "Ошибка очистка файла users_db", false, null, null, $reply_keyboard);
        }

        // strcasecmp — Бинарно-безопасное сравнение строк без учёта регистра
        if(strcasecmp($message_text, '1') == 0)
        {
            $reply_keyboard = new \TelegramBot\Api\Types\ReplyKeyboardMarkup(array(array("one", "two", "three")), true);
    	   	$bot->sendMessage($user_id, "ReplyKeyboardMarkup:",null, false, null, $reply_keyboard);
    	   //	$bot->sendMessage($user_id, 'Lol kek');
        }
        if(strcasecmp($message_text, '2') == 0)
        {
            // не исчезает после ответа
            $reply_keyboard = new \TelegramBot\Api\Types\ReplyKeyboardMarkup([['⏪ Назад']], null, true);
    	   	$bot->sendMessage($user_id, "Введите пару:",false, null, null, $reply_keyboard);

        }
        if(strcasecmp($message_text, '3') == 0)
        {
            $res = $bot->getChatMember('-1001845418299',$user_id);
            if (strcasecmp($res->getStatus(), 'creator') == 0 || strcasecmp($res->getStatus(), 'member') == 0)
    	   	    $bot->sendMessage($user_id, 'You are: '.$res->getStatus());
            
        }
        if(strcasecmp($message_text, '4') == 0)
        {
            $reply_keyboard = new \TelegramBot\Api\Types\ReplyKeyboardMarkup([['✅ Включить', '⛔ Выключить'], ['❓Статус','📊 Статистика'],['🔧 Настройки']], null, true);
            $bot->sendMessage($user_id, 'keyboard', false, null, null, $reply_keyboard);
        }
        // ————————————————

        // ————————————————
        // $bot->sendMessage($user_id, 'Your message: ' . $message->getText());
    }, function () {
        return true;
    });
    
    $bot->run();

} catch (\TelegramBot\Api\Exception $e) {
    $e->getMessage();
}

?>
