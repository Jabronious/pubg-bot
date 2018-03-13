require 'discordrb'
require 'byebug'
require 'json'

file = File.read('bot_info.json')
data_hash = JSON.parse(file)

bot = Discordrb::Bot.new token: data_hash['CLIENT_SECRET'], client_id: data_hash['CLIENT_ID']

bot.message(with_text: '!howlong-help') do |event|
    event.respond 'Type "howlong" and then mention a specific user in the channel'
    event.respond 'Example:'
    event.respond '"howlong"'
    event.respond '@Jabronious'
end

bot.message(with_text: '!howlong') do |event|
    event.respond 'Mention the user you need info about:'
    event.user.await(:user) do |user_mention|
        user_id = user_mention.content.tr('<@>', '').to_i
        mentioned_user = bot.users[user_id]
        event.respond "#{mentioned_user.username} Current Match:"
        event.respond "No Match Data"
        byebug
    end
end

bot.run