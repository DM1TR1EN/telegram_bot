<?php
function ClearUserDb()
{
    if (file_put_contents('users.txt', null) !== false)
        return true;
    return null;
}
function checkUser($searching_user_id)
{
    $users_bd_file_name = 'users.txt';
    $users_db_string = file_get_contents($users_bd_file_name);                  //// Читаем из файла в строку $users_db_string
    // $users_db_string = str_replace(PHP_EOL,'_',$f_get_cont);                //и заменяем PHP_EOL на '_' 
    // $users_db_string = rtrim(str_replace(PHP_EOL,'_',$f_get_cont), "_");    //и заменяем PHP_EOL на '_' и удаляем последний '_' в строке
    
    // Выводим строку
    // echo '<br><br>', '$users_db_string: ', $users_db_string;  
    // echo '<br><br>';
   
    //ищем первое вхождение $searching_user_id в $users_db_string
    $pos    = strpos($users_db_string, $searching_user_id.PHP_EOL);  
    
    if ($pos !== false) 
    {
        // echo "Строка '$searching_user_id' найдена в строке users_db_string в позиции $pos. Код уже был выдан данному юзеру!";
        //юзер уже есть в БД
        return true; 
    } 
    else 
    {
        // echo "Строка '$searching_user_id' не найдена. Добавим её в конец, чтобы была! Можно выдавать код юзеру!";
        file_put_contents($users_bd_file_name, $searching_user_id.PHP_EOL, FILE_APPEND);
        // Новый юзер добавлен в БД
        return false;
    }
}
// $delta_time = 8;
function getVrfCode($delta_time = 3)
{
    $exp_date = date("m_d", strtotime(date('Y-m-d').'+'.$delta_time.' days'));
    // echo '<br><br>';
    // echo '$exp_date: ', $exp_date;
    
    $codes_db_file_name = 'codes_db.txt';
    $codes_db_string = file_get_contents($codes_db_file_name);
    // $codes_db_string = '02_28_diowfn;02_09_ekshqm;02_15_eobisk;02_20_wofksj';
    
    // echo '<br><br>';
    // echo '$codes_db_string: ', $codes_db_string;
    
    $offset    = strpos($codes_db_string, $exp_date);  
    if ($offset !== false) 
    {
        // echo '<br><br>';
        // echo $offset;
        // echo "Строка '$exp_date' найдена в строке codes_db_string в позиции $offset";
        
        // $result = substr($codes_db_string, $offset, 12); 
        // echo '<br><br>';
        // echo "Код доступа: $result";
        return substr($codes_db_string, $offset, 12);
    }
    else
    {
        // echo '<br><br>'.'На указанную дату (текущая + '.$delta_time.' дней) код не найден!';
        return null;
    }
}

// if ($_GET["user"] != null) 
    // // echo "Start";
    // if (!checkUser($_GET["user"]))
        // echo '<br><br>Код доступа: ',getVrfCode();
    // else
        // echo '<br><br>'.date('Y-m-d').' Юзер уже получал код!';
?>