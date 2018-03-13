require 'discordrb'
require 'byebug'
require 'json'

file = File.read('bot_info.json')
data_hash = JSON.parse(file)

bot = Discordrb::Bot.new token: data_hash['CLIENT_SECRET'], client_id: data_hash['CLIENT_ID']

bot.message(with_text: '!howlong-help') do |event|
  event.respond 'There is nothing that I can do yet, sorry boot that!'
end

bot.run